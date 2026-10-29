"""Router de evaluación de modelos de proyección (T-14, D-003).

Expone la misma evaluación que scripts/evaluar_modelos.py sobre el escenario
sintético declarado, para que cualquier interfaz muestre métricas calculadas y no
valores escritos a mano.
"""
from fastapi import APIRouter

from app.core.proyeccion.escenario_sintetico import evaluar_escenario_sintetico

router = APIRouter()


@router.get(
    "/modelos/evaluacion",
    summary="Comparar predictivo, determinista y línea base ingenua (datos sintéticos)",
    description=(
        "Corre la evaluación temporal (folds expansivos + holdout) sobre un escenario "
        "SINTÉTICO y aplica la regla D-003. No son datos de Unibán (D-006, D-019)."
    ),
)
def evaluacion_modelos(semilla: int = 2026) -> dict:
    return evaluar_escenario_sintetico(semilla)
