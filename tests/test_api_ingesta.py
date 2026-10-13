"""Pruebas de los endpoints de ingesta (T-11).

Verifican que la API reciba y valide los payloads del Equipo 1 y Equipo 3
según el contrato de integración (docs/contrato-integracion.md).
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db():
    """Mock o sesión limpia para no depender de PostgreSQL en pruebas de API."""
    class DummyDB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass

    app.dependency_overrides[get_db] = lambda: DummyDB()
    yield
    app.dependency_overrides.clear()


def test_ingesta_aforamiento_valido():
    """Un payload idéntico al del contrato v1 debe ser aceptado con 201."""
    payload = {
        "parcela_id": "P-018",
        "fecha": "2026-09-14",
        "area_ha": 2.4,
        "num_plantas_estimado": 1850,
        "calidad_confianza": 0.87,
    }
    response = client.post("/api/v1/ingesta/aforamiento", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["estado"] == "recibido"
    assert data["tipo"] == "aforamiento"
    assert data["parcela_id"] == "P-018"


def test_ingesta_aforamiento_confianza_fuera_de_rango():
    """calidad_confianza debe estar entre 0.0 y 1.0."""
    payload = {
        "parcela_id": "P-018",
        "fecha": "2026-09-14",
        "area_ha": 2.4,
        "num_plantas_estimado": 1850,
        "calidad_confianza": 1.5,  # Inválido
    }
    response = client.post("/api/v1/ingesta/aforamiento", json=payload)
    assert response.status_code == 422


def test_ingesta_aforamiento_campo_faltante():
    """Si falta un campo obligatorio (ej. calidad_confianza), rechazar con 422."""
    payload = {
        "parcela_id": "P-018",
        "fecha": "2026-09-14",
        "area_ha": 2.4,
        "num_plantas_estimado": 1850,
    }
    response = client.post("/api/v1/ingesta/aforamiento", json=payload)
    assert response.status_code == 422


def test_ingesta_operacion_valida():
    """Un payload de operación idéntico al del contrato v1 debe ser aceptado con 201."""
    payload = {
        "parcela_id": "P-018",
        "acopio_id": "AC-02",
        "tiempo_acarreo_min": 35,
        "medio_acarreo": "cable_via",
        "capacidad_medio_racimos": 65,
        "vehiculos": [{"id": "V-3", "capacidad_racimos": 420}],
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
        "inventario": [{"insumo": "cajas", "cantidad": 300}],
        "consumos": [{"insumo": "cajas", "periodo": "2026-W37", "cantidad": 412}],
    }
    response = client.post("/api/v1/ingesta/operacion", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["estado"] == "recibido"
    assert data["tipo"] == "operacion"
    assert data["parcela_id"] == "P-018"


def test_ingesta_operacion_medio_acarreo_invalido():
    """El medio_acarreo debe ser enum: cable_via, traccion_animal u otro."""
    payload = {
        "parcela_id": "P-018",
        "acopio_id": "AC-02",
        "tiempo_acarreo_min": 35,
        "medio_acarreo": "helicoptero",  # No permitido
        "capacidad_medio_racimos": 65,
        "vehiculos": [{"id": "V-3", "capacidad_racimos": 420}],
        "ventana_despacho": {
            "inicio": "2026-09-21T06:00:00",
            "fin": "2026-09-21T16:00:00",
        },
    }
    response = client.post("/api/v1/ingesta/operacion", json=payload)
    assert response.status_code == 422


def test_ingesta_operacion_ventana_invalida():
    """La ventana fin no puede ser anterior o igual a inicio."""
    payload = {
        "parcela_id": "P-018",
        "acopio_id": "AC-02",
        "tiempo_acarreo_min": 35,
        "medio_acarreo": "cable_via",
        "capacidad_medio_racimos": 65,
        "vehiculos": [{"id": "V-3", "capacidad_racimos": 420}],
        "ventana_despacho": {
            "inicio": "2026-09-21T16:00:00",
            "fin": "2026-09-21T06:00:00",  # Fin antes que inicio
        },
    }
    response = client.post("/api/v1/ingesta/operacion", json=payload)
    assert response.status_code == 422
    assert "fin de la ventana de despacho debe ser posterior" in response.text
