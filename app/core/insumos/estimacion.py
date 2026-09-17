"""Derivación de insumos de empaque a partir del plan de recolección.

    necesidad[i] = volumen_del_plan x consumo_unitario[i] - inventario[i]
        donde i en { cajas, carton, bolsas }

Los coeficientes de consumo son configurables por productor y viven en
config/parametros.yaml. Ver D-004 en DECISIONES.md.

Responsable: Lizbeth — frente backend (T-08)
"""
from dataclasses import dataclass
from datetime import date

INSUMOS = ("cajas", "carton", "bolsas")


@dataclass(frozen=True)
class RequerimientoInsumo:
    insumo: str
    fecha: date
    cantidad_requerida: float
    inventario_disponible: float
    deficit: float


def estimar(
    volumen_racimos: float,
    fecha: date,
    coeficientes: dict[str, float],
    inventario: dict[str, float],
) -> list[RequerimientoInsumo]:
    """Necesidad por insumo para un volumen de cosecha y una fecha dados."""
    raise NotImplementedError("T-08")
