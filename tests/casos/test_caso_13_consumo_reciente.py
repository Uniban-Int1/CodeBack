"""Casos de cálculo manual del resumen de consumos recientes (consumptions[] del Equipo 3)."""
from datetime import date

from fastapi.testclient import TestClient

from app.core.insumos.consumos import resumir_consumos
from app.main import app

client = TestClient(app)


def test_resumen_agrupa_por_insumo_y_compara_con_lo_requerido():
    """T-09 13 — consumos sintéticos de cajas y bolsas.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        cajas: 20 (2026-10-05), 30 (2026-10-19)
        bolsas: 40 (2026-10-12)
        "Urea 46%": 12 (no es empaque, se ignora)
        requerido: cajas 123.76, bolsas 145.6

    Cálculo manual:
        cajas: total 50, 2 registros, promedio 25, último 30 el 19/10,
               diferencia 123.76 - 25 = 98.76
        bolsas: total 40, 1 registro, promedio 40, diferencia 145.6 - 40 = 105.6
        carton: sin registros, no aparece.
    """
    consumos = [
        {"name": "cajas", "quantity": 20, "date": "2026-10-05"},
        {"name": "Cajas de Exportación", "quantity": 30, "date": "2026-10-19"},
        {"name": "bolsas", "quantity": 40, "date": "2026-10-12"},
        {"name": "Urea 46%", "quantity": 12, "date": "2026-10-10"},
    ]
    resumen = {c.insumo: c for c in resumir_consumos(consumos, {"cajas": 123.76, "bolsas": 145.6})}

    assert set(resumen) == {"cajas", "bolsas"}
    assert resumen["cajas"].registros == 2
    assert resumen["cajas"].total == 50.0
    assert resumen["cajas"].promedio_por_registro == 25.0
    assert resumen["cajas"].ultima_fecha == date(2026, 10, 19)
    assert resumen["cajas"].ultima_cantidad == 30.0
    assert resumen["cajas"].diferencia_requerido_vs_promedio == 98.76
    assert resumen["bolsas"].diferencia_requerido_vs_promedio == 105.6


def test_registros_invalidos_se_ignoran():
    consumos = [
        {"name": "cajas", "quantity": -5},
        {"name": "cajas", "quantity": None},
        {"name": "cajas", "quantity": True},
        "no-es-un-registro",
    ]
    assert resumir_consumos(consumos, {"cajas": 10.0}) == []


def test_recomendar_devuelve_consumo_reciente():
    payload = {
        "parcel": {"id": "11111111-1111-4111-8111-111111111111", "areaHa": 2.4},
        "aforamiento": {"period": "2026-W44", "estimatedPlants": 1850, "confidence": 0.87},
        "inventory": [{"name": "cajas", "quantity": 80}],
        "ventana_despacho": {"inicio": "2026-10-30T06:00:00", "fin": "2026-10-30T16:00:00"},
        "consumptions": [{"name": "cajas", "unit": "unidad", "quantity": 20, "date": "2026-10-25"}],
    }
    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 200
    consumo = response.json()["consumo_reciente"]
    assert consumo == [{
        "insumo": "cajas", "registros": 1, "total": 20.0, "promedio_por_registro": 20.0,
        "ultima_fecha": "2026-10-25", "ultima_cantidad": 20.0,
        "requerido": 123.76, "diferencia_requerido_vs_promedio": 103.76,
    }]


def test_recomendar_sin_consumptions_devuelve_lista_vacia():
    payload = {
        "parcela_id": "P-018", "periodo": "2026-W44", "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87, "inventario": {"cajas": 80},
        "ventana_despacho": {"inicio": "2026-10-30T06:00:00", "fin": "2026-10-30T16:00:00"},
    }
    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 200
    assert response.json()["consumo_reciente"] == []
