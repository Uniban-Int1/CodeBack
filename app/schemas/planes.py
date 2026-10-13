"""Esquemas Pydantic para consulta de planes de recolección e insumos.

Cumplen el contrato acordado en docs/contrato-integracion.md.
Responsable: José Miguel — frente front y plataforma (T-12)
"""
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class ItemPlanRespuesta(BaseModel):
    """Detalle de recolección y transporte para una parcela."""
    parcela_id: str = Field(..., description="Identificador acordado de la parcela (ej. P-018)")
    fecha_corte: datetime = Field(..., description="Fecha y hora límite calculada para el corte")
    vehiculo_id: str | None = Field(None, description="Identificador del vehículo asignado")
    orden: int = Field(..., ge=1, description="Orden de acarreo y cargue")
    carga_estimada_racimos: int = Field(..., ge=0, description="Volumen asignado en racimos")
    cumple_ventana: bool = Field(..., description="Indica si la carga llega dentro de la ventana de despacho")
    motivo: str | None = Field(None, description="Motivo de incumplimiento o exclusión, si aplica")


class InsumoRequerimientoRespuesta(BaseModel):
    """Requerimiento y déficit estimado para un insumo de empaque."""
    insumo: str = Field(..., description="Nombre del insumo (cajas, carton, bolsas)")
    fecha: date = Field(..., description="Fecha requerida para el empaque")
    cantidad_requerida: float = Field(..., ge=0, description="Total requerido según volumen proyectado")
    inventario_disponible: float = Field(..., ge=0, description="Saldo disponible en acopio/parcela")
    deficit: float = Field(..., ge=0, description="Cantidad faltante por suministrar")


class MetricasPlanRespuesta(BaseModel):
    """Métricas operativas del plan generado."""
    cumplimiento_ventana: float = Field(
        ..., ge=0.0, le=1.0, description="Proporción de parcelas que cumplen su ventana de despacho"
    )
    uso_capacidad: float = Field(
        ..., ge=0.0, description="Ratio de capacidad utilizada sobre capacidad total de vehículos"
    )


class PlanRecoleccionRespuesta(BaseModel):
    """Respuesta completa del plan entregado al Equipo 3 y frontend."""
    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(..., description="Identificador único del plan (ej. PL-2026-W38)")
    periodo: str = Field(..., description="Semana ISO planificada (ej. 2026-W38)")
    version_metodo: str = Field(..., description="Versión trazable del método generador (D-005)")
    generado_en: datetime = Field(..., description="Marca temporal de generación del plan")
    items: list[ItemPlanRespuesta] = Field(..., description="Secuencia de corte y transporte por parcela")
    insumos: list[InsumoRequerimientoRespuesta] = Field(
        ..., description="Requerimientos consolidados de insumos de empaque"
    )
    metricas: MetricasPlanRespuesta = Field(..., description="Indicadores de cumplimiento y capacidad")


class InsumosConsolidadoRespuesta(BaseModel):
    """Respuesta específica para consulta de insumos por periodo."""
    periodo: str = Field(..., description="Semana ISO consultada")
    version_metodo: str = Field(..., description="Versión del método (D-005)")
    insumos: list[InsumoRequerimientoRespuesta] = Field(..., description="Detalle de insumos y déficit")
