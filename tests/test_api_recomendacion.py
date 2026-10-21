"""Pruebas para el endpoint directo de recomendación de insumos y logística (T-11, T-12).

Verifica que POST /api/v1/recomendar procese aforamiento, inventario y ventana
y devuelva inmediatamente la recomendación sin intermediarios.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_recomendar_exitoso():
    """POST /api/v1/recomendar debe retornar recomendación con status 200."""
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


def test_recomendar_deficit_cajas():
    """Si el inventario es bajo, el déficit debe reflejarse en los insumos."""
    payload = {
        "parcela_id": "P-018",
        "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87,
        "area_ha": 2.4,
        "tiempo_acarreo_min": 35,
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
        "inventario": {
            "cajas": 50.0,  # Menor que lo requerido (~123.8)
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
