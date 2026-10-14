"""Pruebas de la interfaz de usuario Jinja2 (T-15).

Verifican que la ruta raíz (GET /) y la ruta de plan (GET /plan/{periodo})
rendericen HTML correctamente con status 200.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_vista_raiz_renderiza_html():
    """GET / debe responder con HTML y contener elementos del layout."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Plan de recolección y transporte" in response.text
    assert "Semana" in response.text
    assert "Insumos requeridos" in response.text


def test_vista_plan_periodo_especifico():
    """GET /plan/{periodo} debe renderizar el periodo en el título y tablas."""
    response = client.get("/plan/2026-W40")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "2026-W40" in response.text
    assert "Parcela" in response.text
    assert "cajas" in response.text
