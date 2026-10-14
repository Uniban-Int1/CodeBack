"""Punto de entrada de la aplicación FastAPI.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

app.mount("/static", StaticFiles(directory="app/static"), name="static")

from app.api import ingesta, insumos, planes, vistas

app.include_router(vistas.router, tags=["vistas"])
app.include_router(ingesta.router, prefix="/api/v1", tags=["ingesta"])
app.include_router(planes.router, prefix="/api/v1", tags=["planes"])
app.include_router(insumos.router, prefix="/api/v1", tags=["insumos"])


@app.get("/salud", tags=["sistema"])
def salud():
    return {"estado": "ok", "version_metodo": "heuristica-v1"}
