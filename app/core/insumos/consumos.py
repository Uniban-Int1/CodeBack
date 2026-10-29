"""Resumen de consumos recientes de insumos de empaque enviados por el Equipo 3.

El Equipo 3 envía los registros de consumo de la parcela de los últimos 90 días
(`consumptions[]`). Aquí se agrupan por insumo y se ponen al lado de lo que pide la
recomendación, en la misma unidad (sin conversiones, D-015). No recalibra los
coeficientes de consumo: es una referencia para el productor, no un ajuste del modelo.
"""
from dataclasses import dataclass
from datetime import date

INSUMOS_EMPAQUE = ("cajas", "carton", "bolsas")


def nombre_insumo(nombre: object) -> str | None:
    """Mapea el nombre libre del Equipo 3 a cajas/carton/bolsas, o None si no es empaque."""
    texto = str(nombre or "").lower()
    if "caja" in texto:
        return "cajas"
    if "carton" in texto or "cartón" in texto:
        return "carton"
    if "bolsa" in texto:
        return "bolsas"
    return None


@dataclass(frozen=True)
class ConsumoReciente:
    insumo: str
    registros: int
    total: float
    promedio_por_registro: float
    ultima_fecha: date | None
    ultima_cantidad: float | None
    requerido: float | None
    diferencia_requerido_vs_promedio: float | None


def resumir_consumos(consumos: list[dict], requeridos: dict[str, float]) -> list[ConsumoReciente]:
    """Agrupa los consumos por insumo de empaque.

    Ignora registros que no son de empaque o que no traen una cantidad válida (no
    negativa). Una fecha inválida no descarta el registro: solo deja de contar para
    "último consumo".
    """
    agrupados: dict[str, list[tuple[date | None, float]]] = {}
    for registro in consumos or []:
        if not isinstance(registro, dict):
            continue
        insumo = nombre_insumo(registro.get("name") or registro.get("insumo"))
        cantidad = registro.get("quantity", registro.get("cantidad"))
        if insumo is None or isinstance(cantidad, bool) or not isinstance(cantidad, (int, float)) or cantidad < 0:
            continue
        try:
            fecha = date.fromisoformat(str(registro.get("date", ""))[:10])
        except ValueError:
            fecha = None
        agrupados.setdefault(insumo, []).append((fecha, float(cantidad)))

    resumen = []
    for insumo in INSUMOS_EMPAQUE:
        filas = agrupados.get(insumo)
        if not filas:
            continue
        total = sum(cantidad for _, cantidad in filas)
        promedio = total / len(filas)
        con_fecha = [fila for fila in filas if fila[0] is not None]
        ultima = max(con_fecha, key=lambda fila: fila[0]) if con_fecha else None
        requerido = requeridos.get(insumo)
        resumen.append(ConsumoReciente(
            insumo=insumo,
            registros=len(filas),
            total=round(total, 2),
            promedio_por_registro=round(promedio, 2),
            ultima_fecha=ultima[0] if ultima else None,
            ultima_cantidad=round(ultima[1], 2) if ultima else None,
            requerido=requerido,
            diferencia_requerido_vs_promedio=None if requerido is None else round(requerido - promedio, 2),
        ))
    return resumen
