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


def proyectar(aforamiento: Aforamiento, periodo: str, **params) -> ProyeccionCosecha:
    raise NotImplementedError("T-06")
