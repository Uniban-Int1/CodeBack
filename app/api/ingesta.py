"""Router de ingesta.

Recibe datos de aforamiento del Equipo 1 y datos operativos del Equipo 3.
Valida contra el contrato de integración v1 (docs/contrato-integracion.md).

Responsable: José Miguel — frente front y plataforma (T-11)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.ingesta import (
    AforamientoIngesta,
    IngestaRespuesta,
    OperacionIngesta,
)

router = APIRouter()


@router.post(
    "/ingesta/aforamiento",
    response_model=IngestaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Ingesta de aforamiento (Equipo 1)",
    description="Recibe la estimación de conteo y confianza de plantas para una parcela.",
)
def recibir_aforamiento(
    datos: AforamientoIngesta,
    db: Session = Depends(get_db),
) -> IngestaRespuesta:
    """Valida y procesa el aforamiento enviado por el Equipo 1."""
    # Validación semántica adicional
    if datos.num_plantas_estimado == 0 and datos.calidad_confianza > 0:
        # Aceptable o advertible, pero pasa la validación Pydantic
        pass

    return IngestaRespuesta(
        tipo="aforamiento",
        parcela_id=datos.parcela_id,
        mensaje="Aforamiento recibido y validado correctamente.",
    )


@router.post(
    "/ingesta/operacion",
    response_model=IngestaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Ingesta de datos operativos (Equipo 3)",
    description="Recibe parámetros de acarreo, vehículos, ventana de despacho e inventario.",
)
def recibir_operacion(
    datos: OperacionIngesta,
    db: Session = Depends(get_db),
) -> IngestaRespuesta:
    """Valida y procesa los datos operativos enviados por el Equipo 3."""
    if datos.ventana_despacho.fin <= datos.ventana_despacho.inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha/hora de fin de la ventana de despacho debe ser posterior a la de inicio.",
        )

    return IngestaRespuesta(
        tipo="operacion",
        parcela_id=datos.parcela_id,
        mensaje="Datos operativos recibidos y validados correctamente.",
    )
