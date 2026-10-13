"""Esquemas Pydantic para ingesta de datos de equipos 1 y 3.

Contrato acordado v1 en docs/contrato-integracion.md.
Responsable: José Miguel — frente front y plataforma (T-11)
"""
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class AforamientoIngesta(BaseModel):
    """Payload de aforamiento recibido del Equipo 1."""
    model_config = ConfigDict(extra="forbid")

    parcela_id: str = Field(
        ...,
        description="Identificador acordado de parcela (ej. P-018 según D-007)",
        min_length=1,
    )
    fecha: date = Field(..., description="Fecha del aforamiento")
    area_ha: float = Field(..., gt=0, description="Superficie de la parcela en hectáreas")
    num_plantas_estimado: int = Field(
        ..., ge=0, description="Resultado del conteo de plantas"
    )
    calidad_confianza: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza del aforamiento (0.0 a 1.0)",
    )


class VehiculoIngesta(BaseModel):
    id: str = Field(..., description="Identificador o alias del vehículo")
    capacidad_racimos: int = Field(..., gt=0, description="Capacidad en racimos")


class VentanaDespachoIngesta(BaseModel):
    inicio: datetime = Field(..., description="Inicio de la ventana de despacho")
    fin: datetime = Field(..., description="Fin de la ventana de despacho")


class InventarioItemIngesta(BaseModel):
    insumo: str = Field(..., description="Nombre del insumo (ej. cajas, carton, bolsas)")
    cantidad: float = Field(..., ge=0, description="Cantidad disponible")


class ConsumoItemIngesta(BaseModel):
    insumo: str = Field(..., description="Nombre del insumo")
    periodo: str = Field(..., description="Periodo del consumo (ej. 2026-W37)")
    cantidad: float = Field(..., ge=0, description="Cantidad consumida observada")


class OperacionIngesta(BaseModel):
    """Payload de gestión operativa recibido del Equipo 3."""
    model_config = ConfigDict(extra="forbid")

    parcela_id: str = Field(..., description="Identificador de la parcela")
    acopio_id: str = Field(..., description="Identificador del centro de acopio")
    tiempo_acarreo_min: int = Field(
        ..., ge=0, description="Tiempo de acarreo en minutos hacia el acopio"
    )
    medio_acarreo: Literal["cable_via", "traccion_animal", "otro"] = Field(
        ..., description="Medio de transporte interno"
    )
    capacidad_medio_racimos: int = Field(
        ..., gt=0, description="Capacidad por viaje del medio de acarreo"
    )
    vehiculos: list[VehiculoIngesta] = Field(
        ..., min_length=1, description="Vehículos disponibles para el despacho"
    )
    ventana_despacho: VentanaDespachoIngesta = Field(
        ..., description="Ventana de despacho asignada"
    )
    inventario: list[InventarioItemIngesta] = Field(
        default_factory=list, description="Inventario disponible por insumo"
    )
    consumos: list[ConsumoItemIngesta] | None = Field(
        default=None, description="Consumos históricos observados (opcional)"
    )


class IngestaRespuesta(BaseModel):
    """Respuesta estándar para confirmación de ingesta."""
    estado: Literal["recibido"] = "recibido"
    tipo: str
    parcela_id: str
    mensaje: str
    recibido_en: datetime = Field(default_factory=datetime.now)
