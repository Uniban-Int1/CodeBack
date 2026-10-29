"""Punto de entrada de la aplicación FastAPI.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Logística de recolección, transporte e insumos — Plátano/Unibán",
    description=(
        "Genera un plan semanal de recolección y transporte ajustado a las ventanas "
        "de despacho, y deriva de él la necesidad de insumos de empaque."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends

from app.api import ingesta, insumos, modelos, planes, recomendacion
from app.core.seguridad import verificar_token_integracion

# D-010/D-018: la verificación de token solo bloquea si INTEGRACION_TOKEN está configurado
# en el entorno. Se aplica a los endpoints de integración entre servicios.
_dep_integracion = [Depends(verificar_token_integracion)]

app.include_router(
    recomendacion.router, prefix="/api/v1", tags=["recomendacion"], dependencies=_dep_integracion
)
app.include_router(
    ingesta.router, prefix="/api/v1", tags=["ingesta"], dependencies=_dep_integracion
)
app.include_router(
    planes.router, prefix="/api/v1", tags=["planes"], dependencies=_dep_integracion
)
app.include_router(
    insumos.router, prefix="/api/v1", tags=["insumos"], dependencies=_dep_integracion
)
# Solo lectura sobre datos sintéticos declarados: no es un endpoint de integración.
app.include_router(modelos.router, prefix="/api/v1", tags=["modelos"])


@app.get("/salud", tags=["sistema"])
def salud():
    return {"estado": "ok", "version_metodo": "heuristica-v1"}
