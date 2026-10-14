"""Rutas web para renderizar las vistas Jinja2.

Responsable: David (con José Miguel) — frente front y plataforma (T-15).
"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.entidades import PlanRecoleccion

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def obtener_plan_demo(periodo: str = "2026-W38") -> dict:
    """Datos de demostración para visualización cuando no hay registros en base de datos."""
    return {
        "periodo": periodo,
        "version_metodo": "heuristica-v1",
        "items": [
            {
                "parcela_id": "P-018",
                "fecha_corte": datetime(2026, 9, 20, 6, 0).strftime("%Y-%m-%d %H:%M"),
                "vehiculo_id": "V-3",
                "orden": 1,
                "carga_estimada_racimos": 210,
                "cumple_ventana": True,
                "motivo": None,
            },
            {
                "parcela_id": "P-022",
                "fecha_corte": datetime(2026, 9, 20, 7, 30).strftime("%Y-%m-%d %H:%M"),
                "vehiculo_id": "V-3",
                "orden": 2,
                "carga_estimada_racimos": 190,
                "cumple_ventana": True,
                "motivo": None,
            },
            {
                "parcela_id": "P-031",
                "fecha_corte": datetime(2026, 9, 21, 14, 0).strftime("%Y-%m-%d %H:%M"),
                "vehiculo_id": None,
                "orden": 3,
                "carga_estimada_racimos": 150,
                "cumple_ventana": False,
                "motivo": "excede_capacidad_vehiculos",
            },
        ],
        "insumos": [
            {
                "insumo": "cajas",
                "fecha": date(2026, 9, 20),
                "cantidad_requerida": 340.0,
                "inventario_disponible": 250.0,
                "deficit": 90.0,
            },
            {
                "insumo": "carton",
                "fecha": date(2026, 9, 20),
                "cantidad_requerida": 340.0,
                "inventario_disponible": 400.0,
                "deficit": 0.0,
            },
            {
                "insumo": "bolsas",
                "fecha": date(2026, 9, 20),
                "cantidad_requerida": 400.0,
                "inventario_disponible": 350.0,
                "deficit": 50.0,
            },
        ],
    }


@router.get("/", response_class=HTMLResponse, summary="Vista principal del plan")
def vista_inicio(request: Request, db: Session = Depends(get_db)):
    """Muestra el plan más reciente o datos de demostración."""
    periodo = "2026-W38"
    try:
        ultimo_plan = db.query(PlanRecoleccion).order_by(PlanRecoleccion.id.desc()).first()
        if ultimo_plan:
            periodo = ultimo_plan.periodo
    except Exception:
        pass
    return vista_plan(request=request, periodo=periodo, db=db)


@router.get("/plan/{periodo}", response_class=HTMLResponse, summary="Vista de plan por periodo")
def vista_plan(request: Request, periodo: str, db: Session = Depends(get_db)):
    """Renderiza el plan de recolección e insumos para el periodo solicitado."""
    plan_db = None
    try:
        plan_db = (
            db.query(PlanRecoleccion)
            .filter(PlanRecoleccion.periodo == periodo)
            .order_by(PlanRecoleccion.id.desc())
            .first()
        )
    except Exception:
        plan_db = None

    class PlanVistaObj:
        def __init__(self, periodo, version_metodo, items):
            self.periodo = periodo
            self.version_metodo = version_metodo
            self.items = items

    if plan_db:
        items = [
            {
                "parcela_id": it.parcela_id,
                "fecha_corte": it.fecha_corte.strftime("%Y-%m-%d %H:%M"),
                "vehiculo_id": str(it.vehiculo_id) if it.vehiculo_id else "—",
                "orden": it.orden,
                "carga_estimada_racimos": it.carga_estimada_racimos,
                "cumple_ventana": it.cumple_ventana,
                "motivo": it.motivo,
            }
            for it in plan_db.items
        ]
        insumos = [
            {
                "insumo": req.insumo.nombre if hasattr(req, "insumo") and req.insumo else f"insumo-{req.insumo_id}",
                "fecha": req.fecha.date(),
                "cantidad_requerida": float(req.cantidad_requerida),
                "inventario_disponible": 0.0,
                "deficit": float(req.deficit),
            }
            for req in plan_db.requerimientos
        ]
        plan_obj = PlanVistaObj(
            periodo=plan_db.periodo,
            version_metodo=plan_db.version_metodo,
            items=items,
        )
    else:
        demo = obtener_plan_demo(periodo)
        plan_obj = PlanVistaObj(
            periodo=demo["periodo"],
            version_metodo=demo["version_metodo"],
            items=demo["items"],
        )
        insumos = demo["insumos"]

    return templates.TemplateResponse(
        request=request,
        name="plan.html",
        context={
            "plan": plan_obj,
            "insumos": insumos,
        },
    )
