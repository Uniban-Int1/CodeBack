"""Pruebas del escenario sintético de evaluación de modelos (T-14, D-003)."""
from math import isfinite

from fastapi.testclient import TestClient

from app.core.proyeccion.escenario_sintetico import evaluar_escenario_sintetico, generar_observaciones
from app.main import app

client = TestClient(app)


def test_generacion_es_reproducible_con_la_misma_semilla():
    assert generar_observaciones(7).equals(generar_observaciones(7))
    assert not generar_observaciones(7).equals(generar_observaciones(8))


def test_evaluacion_compara_los_tres_metodos_en_todos_los_bloques():
    r = evaluar_escenario_sintetico(2026)
    bloques = r["bloques"] + [r["holdout"]]
    assert len(r["bloques"]) == r["supuestos"]["num_folds"]
    for b in bloques:
        assert b["n_comparadas"] > 0
        for clave in ("mae_predictivo", "mae_determinista", "mae_ingenua"):
            assert isfinite(b[clave]) and b[clave] >= 0


def test_decision_d003_es_coherente_con_las_metricas_del_holdout():
    r = evaluar_escenario_sintetico(2026)
    h = r["holdout"]
    esperado = h["mae_predictivo"] < h["mae_determinista"] and h["mae_predictivo"] < h["mae_ingenua"]
    assert r["decision_d003"]["predictivo_supera_a_ambos_en_holdout"] is esperado
    assert r["metodo_en_produccion"] == "determinista-v1"


def test_endpoint_declara_que_los_datos_son_sinteticos():
    response = client.get("/api/v1/modelos/evaluacion")
    assert response.status_code == 200
    data = response.json()
    assert "sintéticos" in data["advertencia"]
    assert data["holdout"]["n_comparadas"] > 0
