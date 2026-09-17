"""Proyección determinista de cosecha por parcela y semana.

Sin machine learning. Es el piso del sistema: funciona desde la semana 8 y es la
referencia contra la que se mide el modelo predictivo (D-003).

Entradas: aforamiento de la parcela y edad de racimo.
La literatura (Arrieta-Escobar et al., 2026) señala la edad de racimo entre 8 y 13
semanas como la variable dominante para el horizonte semanal.

Responsable: Camilo — frente backend (T-06)
"""
from dataclasses import dataclass

METODO = "determinista-v1"


@dataclass(frozen=True)
class Aforamiento:
    parcela_id: str
    num_plantas: int
    area_ha: float
    calidad_confianza: float


@dataclass(frozen=True)
class ProyeccionCosecha:
    parcela_id: str
    periodo: str                  # ISO week, p. ej. "2026-W38"
    volumen_racimos: float
    metodo: str = METODO


def proyectar(
    aforamiento: Aforamiento,
    periodo: str,
    ciclo_racimo_semanas: float,
    factor_perdida: float = 0.0,
) -> ProyeccionCosecha:
    """Estima el volumen de racimos esperado de una parcela en un periodo semanal.

    Supuesto del modelo determinista: cada planta completa su ciclo de racimo una vez
    cada `ciclo_racimo_semanas` semanas, así que en una semana cualquiera se espera que
    una fracción `1 / ciclo_racimo_semanas` de las plantas aforadas esté lista para corte.
    Se pondera por la confianza del aforamiento y se descuenta la merma esperada entre
    el aforamiento y el corte.

        volumen = num_plantas * (1 / ciclo_racimo_semanas) * calidad_confianza * (1 - factor_perdida)

    Lanza ValueError si algún parámetro de entrada es inválido (no hay aforamiento
    negativo, ciclo cero, ni confianza fuera de [0, 1]).
    """
    if aforamiento.num_plantas < 0:
        raise ValueError("num_plantas no puede ser negativo")
    if not 0.0 <= aforamiento.calidad_confianza <= 1.0:
        raise ValueError("calidad_confianza debe estar en [0, 1]")
    if ciclo_racimo_semanas <= 0:
        raise ValueError("ciclo_racimo_semanas debe ser positivo")
    if not 0.0 <= factor_perdida <= 1.0:
        raise ValueError("factor_perdida debe estar en [0, 1]")

    tasa_semanal = 1 / ciclo_racimo_semanas
    volumen = (
        aforamiento.num_plantas
        * tasa_semanal
        * aforamiento.calidad_confianza
        * (1 - factor_perdida)
    )
    return ProyeccionCosecha(
        parcela_id=aforamiento.parcela_id,
        periodo=periodo,
        volumen_racimos=round(volumen, 1),
    )
