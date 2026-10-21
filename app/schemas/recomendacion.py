"""Esquemas Pydantic para el endpoint directo de recomendación de insumos y logística.

Permite al Equipo 3 enviar aforamiento, ventanas e inventario y recibir
inmediatamente el plan de corte y requerimiento de empaque en la misma respuesta.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingesta import VentanaDespachoIngesta
from app.schemas.planes import (
    InsumoRequerimientoRespuesta,
    ItemPlanRespuesta,
    MetricasPlanRespuesta,
)


class SolicitudRecomendacion(BaseModel):
    """Payload enviado por el Equipo 3 para obtener recomendación inmediata."""
    model_config = ConfigDict(extra="forbid")

    parcela_id: str = Field(..., description="Identificador de la parcela (ej. P-018)")
    periodo: str = Field(default="2026-W38", description="Periodo o semana ISO (ej. 2026-W38)")
    num_plantas_estimado: int = Field(..., ge=0, description="Plantas aforadas por el Equipo 1")
    calidad_confianza: float = Field(default=0.87, ge=0.0, le=1.0, description="Confianza del aforamiento")
    area_ha: float = Field(default=2.4, gt=0, description="Superficie de la parcela en ha")
    tiempo_acarreo_min: int = Field(default=35, ge=0, description="Tiempo de acarreo al acopio en minutos")
    ventana_despacho: VentanaDespachoIngesta = Field(..., description="Ventana de despacho asignada")
    inventario: dict[str, float] = Field(
        default_factory=lambda: {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0},
        description="Inventario disponible por insumo",
    )
    vehiculo_id: str | None = Field(default="V-3", description="Vehículo asignado opcional")
    capacidad_vehiculo_racimos: int = Field(default=420, gt=0, description="Capacidad del vehículo")


class RespuestaRecomendacion(BaseModel):
    """Respuesta directa entregada al Equipo 3."""
    parcela_id: str
    periodo: str
    volumen_racimos: float
    fecha_limite_corte: datetime
    cumple_ventana: bool
    version_metodo: str
    item_plan: ItemPlanRespuesta
    insumos: list[InsumoRequerimientoRespuesta]
    metricas: MetricasPlanRespuesta
