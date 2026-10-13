"""Pruebas de los endpoints de consulta de planes e insumos (T-12).

Verifican que GET /api/v1/planes/{periodo}, GET /api/v1/insumos/{periodo}
y GET /api/v1/parametros respondan según el contrato de integración.
"""
from datetime import datetime
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db
from app.models.entidades import ItemPlan, PlanRecoleccion, RequerimientoInsumo, Insumo

client = TestClient(app)


class MockQuery:
    def __init__(self, item=None):
        self._item = item

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._item


class MockDB:
    def __init__(self, plan=None):
        self._plan = plan

    def query(self, model):
        if model == PlanRecoleccion:
            return MockQuery(self._plan)
        return MockQuery(None)


def test_consultar_parametros():
    """GET /api/v1/parametros debe retornar la configuración sin requerir BD."""
    response = client.get("/api/v1/parametros")
    assert response.status_code == 200
    data = response.json()
    assert "parametros" in data
    assert "origen" in data
    assert "consumo_unitario" in data["parametros"]


def test_consultar_plan_no_encontrado():
    """Si no hay plan para el periodo, debe responder 404."""
    app.dependency_overrides[get_db] = lambda: MockDB(plan=None)
    response = client.get("/api/v1/planes/2026-W99")
    assert response.status_code == 404
    assert "No se encontró ningún plan" in response.text
    app.dependency_overrides.clear()


def test_consultar_plan_existente():
    """Si existe un plan en BD, debe formatearlo exactamente como el contrato v1."""
    # Simulamos un plan guardado
    plan_mock = PlanRecoleccion(
        id=42,
        periodo="2026-W38",
        generado_en=datetime(2026, 9, 17, 9, 12, 0),
        version_metodo="heuristica-v1",
    )
    item_mock = ItemPlan(
        id=1,
        plan_id=42,
        parcela_id="P-018",
        fecha_corte=datetime(2026, 9, 20, 6, 0),
        vehiculo_id=1,
        orden=1,
        carga_estimada_racimos=210,
        cumple_ventana=True,
        motivo=None,
    )
    insumo_entidad = Insumo(id=1, nombre="cajas", unidad="caja")
    req_mock = RequerimientoInsumo(
        id=1,
        plan_id=42,
        insumo_id=1,
        fecha=datetime(2026, 9, 20),
        cantidad_requerida=412.0,
        deficit=112.0,
    )
    req_mock.insumo = insumo_entidad

    plan_mock.items = [item_mock]
    plan_mock.requerimientos = [req_mock]

    app.dependency_overrides[get_db] = lambda: MockDB(plan=plan_mock)

    response = client.get("/api/v1/planes/2026-W38")
    assert response.status_code == 200
    data = response.json()

    assert data["plan_id"] == "PL-42"
    assert data["periodo"] == "2026-W38"
    assert data["version_metodo"] == "heuristica-v1"
    assert len(data["items"]) == 1
    assert data["items"][0]["parcela_id"] == "P-018"
    assert data["items"][0]["cumple_ventana"] is True
    assert len(data["insumos"]) == 1
    assert data["insumos"][0]["insumo"] == "cajas"
    assert data["insumos"][0]["deficit"] == 112.0
    assert "metricas" in data
    assert data["metricas"]["cumplimiento_ventana"] == 1.0

    app.dependency_overrides.clear()


def test_consultar_insumos_existente():
    """GET /api/v1/insumos/{periodo} debe retornar el consolidado de requerimientos."""
    plan_mock = PlanRecoleccion(
        id=42,
        periodo="2026-W38",
        generado_en=datetime(2026, 9, 17, 9, 12, 0),
        version_metodo="heuristica-v1",
    )
    insumo_entidad = Insumo(id=1, nombre="cajas", unidad="caja")
    req_mock = RequerimientoInsumo(
        id=1,
        plan_id=42,
        insumo_id=1,
        fecha=datetime(2026, 9, 20),
        cantidad_requerida=300.0,
        deficit=50.0,
    )
    req_mock.insumo = insumo_entidad
    plan_mock.items = []
    plan_mock.requerimientos = [req_mock]

    app.dependency_overrides[get_db] = lambda: MockDB(plan=plan_mock)

    response = client.get("/api/v1/insumos/2026-W38")
    assert response.status_code == 200
    data = response.json()
    assert data["periodo"] == "2026-W38"
    assert len(data["insumos"]) == 1
    assert data["insumos"][0]["insumo"] == "cajas"
    assert data["insumos"][0]["deficit"] == 50.0

    app.dependency_overrides.clear()
