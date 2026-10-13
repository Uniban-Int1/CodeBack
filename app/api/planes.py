"""Router de consulta de planes de recolección y transporte.

Entrega al Equipo 3 y a la interfaz el plan semanal optimizado.
Responsable: José Miguel — frente front y plataforma (T-12)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.entidades import PlanRecoleccion
from app.schemas.planes import (
    InsumoRequerimientoRespuesta,
    ItemPlanRespuesta,
    MetricasPlanRespuesta,
    PlanRecoleccionRespuesta,
)

router = APIRouter()


@router.get(
    "/planes/{periodo}",
    response_model=PlanRecoleccionRespuesta,
    summary="Consultar plan de recolección",
    description="Obtiene el plan de corte, transporte, insumos y métricas para un periodo dado.",
)
def consultar_plan(
    periodo: str,
    db: Session = Depends(get_db),
) -> PlanRecoleccionRespuesta:
    """Busca en base de datos el plan para el periodo o genera la estructura contratada."""
    plan_db = (
        db.query(PlanRecoleccion)
        .filter(PlanRecoleccion.periodo == periodo)
        .order_by(PlanRecoleccion.id.desc())
        .first()
    )

    if plan_db:
        items_resp = [
            ItemPlanRespuesta(
                parcela_id=it.parcela_id,
                fecha_corte=it.fecha_corte,
                vehiculo_id=str(it.vehiculo_id) if it.vehiculo_id is not None else None,
                orden=it.orden,
                carga_estimada_racimos=it.carga_estimada_racimos,
                cumple_ventana=it.cumple_ventana,
                motivo=it.motivo,
            )
            for it in plan_db.items
        ]
        insumos_resp = [
            InsumoRequerimientoRespuesta(
                insumo=req.insumo.nombre if hasattr(req, "insumo") and req.insumo else f"insumo-{req.insumo_id}",
                fecha=req.fecha.date(),
                cantidad_requerida=float(req.cantidad_requerida),
                inventario_disponible=0.0,
                deficit=float(req.deficit),
            )
            for req in plan_db.requerimientos
        ]
        cumplimiento = (
            sum(1 for i in items_resp if i.cumple_ventana) / len(items_resp)
            if items_resp
            else 0.0
        )
        return PlanRecoleccionRespuesta(
            plan_id=f"PL-{plan_db.id}",
            periodo=plan_db.periodo,
            version_metodo=plan_db.version_metodo,
            generado_en=plan_db.generado_en,
            items=items_resp,
            insumos=insumos_resp,
            metricas=MetricasPlanRespuesta(
                cumplimiento_ventana=round(cumplimiento, 2),
                uso_capacidad=0.85,
            ),
        )

    # Si no existe aún en BD para ese periodo, responder 404 claro
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No se encontró ningún plan de recolección para el periodo '{periodo}'.",
    )
