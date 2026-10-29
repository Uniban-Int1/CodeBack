"""Pruebas para el endpoint directo de recomendación de insumos y logística (T-11, T-12).

Verifica que POST /api/v1/recomendar procese tanto el payload canónico
como el payload anidado del Equipo 3 (parcel, aforamiento, inventory).
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_recomendar_exitoso():
    """POST /api/v1/recomendar debe retornar recomendación con status 200 en formato directo."""
    payload = {
        "parcela_id": "P-018",
        "periodo": "2026-W38",
        "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87,
        "area_ha": 2.4,
        "tiempo_acarreo_min": 35,
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
        "inventario": {
            "cajas": 300.0,
            "carton": 400.0,
            "bolsas": 350.0,
        },
        "vehiculo_id": "V-3",
        "capacidad_vehiculo_racimos": 420,
    }

    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["parcela_id"] == "P-018"
    assert data["periodo"] == "2026-W38"
    assert data["volumen_racimos"] == 145.6
    assert data["cumple_ventana"] is True
    assert data["version_metodo"] == "determinista-v1"
    assert len(data["insumos"]) == 3
    assert data["item_plan"]["vehiculo_id"] == "V-3"
    assert data["metricas"]["cumplimiento_ventana"] == 1.0


def test_recomendar_formato_equipo3_anidado():
    """POST /api/v1/recomendar debe aceptar el payload del Equipo 3 cuando trae
    todos los datos obligatorios (incluida ventana_despacho)."""
    payload_equipo3 = {
        "producerId": "e3b0c442-98fc-1c14-9a41-000000000001",
        "parcel": {
            "id": "e3b0c442-98fc-1c14-9a41-000000000002",
            "name": "La Esperanza",
            "areaHa": 2.40,
            "activeCycle": {
                "id": "e3b0c442-98fc-1c14-9a41-000000000003",
                "startDate": "2026-01-15",
                "status": "PRODUCCION",
            },
        },
        "aforamiento": {
            "date": "2026-10-29",
            "period": "2026-W44",
            "estimatedPlants": 1850,
            "confidence": 0.87,
        },
        "inventory": [
            {
                "supplyId": "uuid-1",
                "name": "Cajas de Exportación",
                "category": "Empaque",
                "unit": "unidad",
                "quantity": 100.0,
            },
            {
                "supplyId": "uuid-2",
                "name": "Urea 46%",
                "category": "Fertilizante",
                "unit": "kg",
                "quantity": 82.5,
            },
        ],
        "consumptions": [
            {
                "supplyId": "uuid-2",
                "name": "Urea 46%",
                "unit": "kg",
                "quantity": 12.5,
                "date": "2026-10-05",
            }
        ],
        "losses": [
            {
                "supplyId": "uuid-2",
                "name": "Urea 46%",
                "unit": "kg",
                "quantity": 2.0,
                "date": "2026-10-10",
                "reason": "CLIMA",
            }
        ],
        "ventana_despacho": {
            "inicio": "2026-10-29T06:00:00",
            "fin": "2026-10-29T16:00:00",
        },
    }

    response = client.post("/api/v1/recomendar", json=payload_equipo3)
    assert response.status_code == 200
    data = response.json()

    assert data["parcela_id"] == "e3b0c442-98fc-1c14-9a41-000000000002"
    assert data["periodo"] == "2026-W44"
    assert data["volumen_racimos"] == 145.6
    assert data["cumple_ventana"] is True
    # Verificamos que cajas tenga el inventario de 100 que ellos mandaron
    cajas_req = next(i for i in data["insumos"] if i["insumo"] == "cajas")
    assert cajas_req["inventario_disponible"] == 100.0
    assert cajas_req["deficit"] > 0  # Requerido ~123.8 - 100 = 23.8 déficit


def test_recomendar_formato_equipo3_sin_ventana_falla_con_error_claro():
    """Regla 4 del contrato: si el Equipo 3 no envía ventana_despacho, el servicio
    debe reportarlo (422 con el nombre del campo), no inventar un horario fijo.

    Este es el payload real que envió el Equipo 3 en su propuesta de integración
    (sin ventana_despacho ni tiempo_acarreo_min)."""
    payload_equipo3_real = {
        "producerId": "33333333-3333-4333-8333-333333333333",
        "parcel": {"id": "11111111-1111-4111-8111-111111111111", "name": "La Esperanza", "areaHa": 2.4},
        "aforamiento": {
            "date": "2026-10-29",
            "period": "2026-W44",
            "estimatedPlants": 1850,
            "confidence": 0.87,
        },
        "inventory": [
            {"name": "cajas", "unit": "unidad", "quantity": 80},
            {"name": "carton", "unit": "unidad", "quantity": 120},
            {"name": "bolsas", "unit": "unidad", "quantity": 200},
        ],
    }

    response = client.post("/api/v1/recomendar", json=payload_equipo3_real)
    assert response.status_code == 422
    assert "ventana_despacho" in response.text


def test_recomendar_confianza_null_responde_422_no_500():
    """El contrato Equipo 1 -> Equipo 3 permite confidence null; debe reportarse como faltante, no reventar."""
    payload = {
        "parcel": {"id": "11111111-1111-4111-8111-111111111111", "areaHa": 2.4},
        "aforamiento": {"date": "2026-10-27", "period": "2026-W44", "estimatedPlants": 1850, "confidence": None},
        "inventory": [{"name": "cajas", "quantity": 80}],
        "ventana_despacho": {"inicio": "2026-10-30T06:00:00", "fin": "2026-10-30T16:00:00"},
    }
    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 422
    assert "calidad_confianza" in response.text


def test_recomendar_sin_datos_obligatorios_lista_todo_lo_que_falta():
    """Un payload vacío debe reportar TODOS los campos obligatorios ausentes, no solo el primero."""
    response = client.post("/api/v1/recomendar", json={})
    assert response.status_code == 422
    detalle = response.text
    for campo in (
        "parcela_id",
        "periodo",
        "num_plantas_estimado",
        "calidad_confianza",
        "inventario",
        "ventana_despacho",
    ):
        assert campo in detalle


def test_recomendar_deficit_cajas():
    """Si el inventario es bajo, el déficit debe reflejarse en los insumos."""
    payload = {
        "parcela_id": "P-018",
        "periodo": "2026-W38",
        "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87,
        "area_ha": 2.4,
        "tiempo_acarreo_min": 35,
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
        "inventario": {
            "cajas": 50.0,
            "carton": 400.0,
            "bolsas": 350.0,
        },
    }

    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 200
    data = response.json()

    cajas_req = next(i for i in data["insumos"] if i["insumo"] == "cajas")
    assert cajas_req["deficit"] > 0
    assert cajas_req["inventario_disponible"] == 50.0


def test_recomendar_ventana_invalida():
    """Ventana donde fin <= inicio debe retornar 422."""
    payload = {
        "parcela_id": "P-018",
        "num_plantas_estimado": 1850,
        "ventana_despacho": {
            "inicio": "2026-09-21T16:00:00",
            "fin": "2026-09-21T06:00:00",
        },
    }

    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 422
