"""Cálculo de la fecha límite de corte.

    fecha_limite = ventana_despacho - tiempo_empaque - tiempo_acarreo

Es la pieza más pequeña del sistema y la más importante: todo el plan se deduce de aquí.
La ventana la fija el embarque; la fecha de corte NO es una decisión libre.

Responsable: Lizbeth — frente backend (T-07)
"""
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class VentanaDespacho:
    inicio: datetime
    fin: datetime


class VentanaInalcanzable(Exception):
    """El acarreo y el empaque no caben antes del cierre de la ventana."""


def fecha_limite_corte(
    ventana: VentanaDespacho,
    minutos_empaque: int,
    minutos_acarreo: int,
    margen_seguridad_min: int = 0,
) -> datetime:
    """Devuelve el instante más tardío en que se puede cortar y aún alcanzar la ventana.

    Lanza VentanaInalcanzable si el resultado cae antes del inicio de la ventana,
    es decir, si la parcela no alcanza a despacharse en ese periodo.
    """
    holgura_total = timedelta(
        minutes=minutos_empaque + minutos_acarreo + margen_seguridad_min
    )
    limite = ventana.fin - holgura_total
    if limite < ventana.inicio:
        raise VentanaInalcanzable(
            f"el acarreo ({minutos_acarreo} min) y el empaque ({minutos_empaque} min) "
            f"no caben antes del cierre de la ventana ({ventana.fin.isoformat()})"
        )
    return limite
