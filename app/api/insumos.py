"""Router de consulta de insumos y parámetros configurables.

Responsable: José Miguel — frente front y plataforma (T-12)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import parametros
from app.db import get_db
from app.models.entidades import PlanRecoleccion
from app.schemas.planes import InsumoRequerimientoRespuesta, InsumosConsolidadoRespuesta

router = APIRouter()


@router.get(
    "/insumos/{periodo}",
    response_model=InsumosConsolidadoRespuesta,
    summary="Consultar insumos y déficit por periodo",
    description="Entrega el consolidado de cajas, cartón y bolsas requeridos y el déficit calculado.",
)
def consultar_insumos(
    periodo: str,
    db: Session = Depends(get_db),
) -> InsumosConsolidadoRespuesta:
    """Retorna los requerimientos de insumos derivados del plan del periodo."""
    plan_db = (
        db.query(PlanRecoleccion)
        .filter(PlanRecoleccion.periodo == periodo)
        .order_by(PlanRecoleccion.id.desc())
        .first()
    )

    if not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron insumos para el periodo '{periodo}'. Plan no disponible.",
        )

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

    return InsumosConsolidadoRespuesta(
        periodo=periodo,
        version_metodo=plan_db.version_metodo,
        insumos=insumos_resp,
    )


@router.get(
    "/parametros",
    summary="Consultar supuestos y parámetros configurables",
    description="Expone los parámetros del dominio (D-004) como tiempos, capacidades y coeficientes.",
)
def consultar_parametros() -> dict:
    """Devuelve los parámetros de dominio cargados de config/parametros.yaml."""
    return {
        "origen": "config/parametros.yaml",
        "parametros": parametros(),
    }
