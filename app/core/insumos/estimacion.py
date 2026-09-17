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
    """Necesidad por insumo para un volumen de cosecha y una fecha dados.

    Para cada insumo en `coeficientes`:
        cantidad_requerida = volumen_racimos * coeficientes[insumo]
        deficit            = max(0, cantidad_requerida - inventario.get(insumo, 0))

    El déficit nunca es negativo: un sobrante de inventario no es un déficit, es
    inventario que se descuenta en el siguiente periodo (fuera del alcance de esta función).
    """
    if volumen_racimos < 0:
        raise ValueError("volumen_racimos no puede ser negativo")

    resultados = []
    for insumo, coeficiente in coeficientes.items():
        if coeficiente < 0:
            raise ValueError(f"coeficiente de '{insumo}' no puede ser negativo")
        cantidad_requerida = volumen_racimos * coeficiente
        disponible = inventario.get(insumo, 0.0)
        deficit = max(0.0, cantidad_requerida - disponible)
        resultados.append(
            RequerimientoInsumo(
                insumo=insumo,
                fecha=fecha,
                cantidad_requerida=round(cantidad_requerida, 2),
                inventario_disponible=disponible,
                deficit=round(deficit, 2),
            )
        )
    return resultados
