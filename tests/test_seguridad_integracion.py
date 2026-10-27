"""Pruebas de la verificación de token entre servicios (D-010, D-018).

Sin INTEGRACION_TOKEN configurado, no debe bloquear nada (no romper la integración
en curso). Con INTEGRACION_TOKEN configurado, debe exigir el token correcto.
"""
import importlib
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db


@pytest.fixture(autouse=True)
def override_db():
    class DummyDB:
        def add(self, obj):
            pass

        def commit(self):
            pass

        def refresh(self, obj):
            pass

    app.dependency_overrides[get_db] = lambda: DummyDB()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_sin_token_configurado_no_bloquea():
    """Hoy, sin INTEGRACION_TOKEN en el entorno, la recomendación funciona sin cabecera."""
    os.environ.pop("INTEGRACION_TOKEN", None)
    payload = {
        "parcela_id": "P-018",
        "periodo": "2026-W38",
        "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87,
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
        "inventario": {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0},
    }
    response = client.post("/api/v1/recomendar", json=payload)
    assert response.status_code == 200


def test_con_token_configurado_rechaza_sin_cabecera():
    """Una vez activado INTEGRACION_TOKEN, una petición sin Authorization debe fallar con 401."""
    os.environ["INTEGRACION_TOKEN"] = "secreto-de-prueba"
    try:
        payload = {
            "parcela_id": "P-018",
            "periodo": "2026-W38",
            "num_plantas_estimado": 1850,
            "calidad_confianza": 0.87,
            "ventana_despacho": {
                "inicio": "2026-09-21T06:00:00",
                "fin": "2026-09-21T16:00:00",
            },
            "inventario": {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0},
        }
        response = client.post("/api/v1/recomendar", json=payload)
        assert response.status_code == 401
    finally:
        os.environ.pop("INTEGRACION_TOKEN", None)


def test_con_token_configurado_acepta_token_correcto():
    os.environ["INTEGRACION_TOKEN"] = "secreto-de-prueba"
    try:
        payload = {
            "parcela_id": "P-018",
            "periodo": "2026-W38",
            "num_plantas_estimado": 1850,
            "calidad_confianza": 0.87,
            "ventana_despacho": {
                "inicio": "2026-09-21T06:00:00",
                "fin": "2026-09-21T16:00:00",
            },
            "inventario": {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0},
        }
        response = client.post(
            "/api/v1/recomendar",
            json=payload,
            headers={"Authorization": "Bearer secreto-de-prueba"},
        )
        assert response.status_code == 200
    finally:
        os.environ.pop("INTEGRACION_TOKEN", None)
