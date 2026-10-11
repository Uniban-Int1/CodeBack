"""Orquestación de parámetros y funciones puras del dominio.

Responsable: Camilo — frente backend (T-08)
"""
from dataclasses import dataclass
from datetime import datetime

from app.config import parametros
from app.core.insumos.estimacion import RequerimientoInsumo, estimar
from app.core.programacion.fechas import VentanaDespacho, fecha_limite_corte
from app.core.proyeccion.base import Aforamiento, proyectar


@dataclass(frozen=True)
class RecomendacionInsumos:
    parcela_id: str
    periodo: str
    volumen_racimos: float
    fecha_limite_corte: datetime
    requerimientos: list[RequerimientoInsumo]
    version_metodo: str


def recomendar_insumos(
    aforamiento: Aforamiento,
    ventana: VentanaDespacho,
    inventario: dict[str, float],
    periodo: str,
    minutos_acarreo: int,
    params: dict | None = None,
) -> RecomendacionInsumos:
    """Construye una recomendación usando los parámetros configurados del dominio.

    Si `params` es None, los parámetros se cargan desde `parametros()`. El argumento
    `minutos_acarreo` es obligatorio porque depende de la parcela y no del flujo base.
    Las funciones de dominio reciben valores explícitos y conservan su pureza.
    """
    if params is None:
        params = parametros()

    proyeccion = proyectar(
        aforamiento,
        periodo=periodo,
        ciclo_racimo_semanas=params["proyeccion"]["ciclo_racimo_semanas"],
        factor_perdida=params["proyeccion"]["factor_perdida"],
    )
    limite_corte = fecha_limite_corte(
        ventana,
        minutos_empaque=params["empaque"]["minutos_por_parcela"],
        minutos_acarreo=minutos_acarreo,
        margen_seguridad_min=params["planificacion"]["margen_seguridad_min"],
    )
    requerimientos = estimar(
        volumen_racimos=proyeccion.volumen_racimos,
        fecha=limite_corte.date(),
        coeficientes=params["consumo_unitario"],
        inventario=inventario,
    )
    return RecomendacionInsumos(
        parcela_id=proyeccion.parcela_id,
        periodo=proyeccion.periodo,
        volumen_racimos=proyeccion.volumen_racimos,
        fecha_limite_corte=limite_corte,
        requerimientos=requerimientos,
        version_metodo=proyeccion.metodo,
    )
