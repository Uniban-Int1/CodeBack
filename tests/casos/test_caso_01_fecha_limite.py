"""Caso 01 — fecha límite de corte, situación normal.

Entradas:
    ventana de despacho: 2026-09-21 06:00 a 16:00
    tiempo de empaque:   120 min
    tiempo de acarreo:    35 min
    margen de seguridad:  30 min

Cálculo a mano:
    holgura total = 120 + 35 + 30 = 185 min = 3 h 05 min
    16:00 - 3 h 05 min = 12:55 del 2026-09-21

Resultado esperado: 2026-09-21 12:55
"""
from datetime import datetime

import pytest

from app.core.programacion.fechas import (
    VentanaDespacho,
    VentanaInalcanzable,
    fecha_limite_corte,
)


def test_fecha_limite_situacion_normal():
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )
    resultado = fecha_limite_corte(
        ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=30
    )
    assert resultado == datetime(2026, 9, 21, 12, 55)


def test_fecha_limite_ventana_ya_paso():
    """Caso 01b — la ventana ya pasó cuando se consulta.

    Entradas:
        ventana:  2026-09-10 06:00 a 16:00 (ya pasada respecto a "hoy" del sistema)
        empaque:  120 min, acarreo: 35 min, margen: 30 min

    Cálculo a mano:
        holgura total = 120 + 35 + 30 = 185 min = 3 h 05 min
        16:00 - 3 h 05 min = 12:55 del 2026-09-10.
        Ese instante ya pasó, pero fecha_limite_corte no conoce "hoy": solo calcula
        el límite teórico. Es responsabilidad del llamador (T-10) comparar ese límite
        contra la fecha actual y descartar la parcela si ya no es alcanzable.

    Resultado esperado: 2026-09-10 12:55 (fecha límite calculada, aunque ya pasada).
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 10, 6, 0),
        fin=datetime(2026, 9, 10, 16, 0),
    )
    resultado = fecha_limite_corte(
        ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=30
    )
    assert resultado == datetime(2026, 9, 10, 12, 55)


def test_fecha_limite_acarreo_mayor_que_ventana():
    """Caso 01c — el acarreo y el empaque no caben dentro de la ventana.

    Entradas:
        ventana:  2026-09-21 06:00 a 08:00 (2 horas = 120 min de ancho)
        empaque:  120 min, acarreo: 35 min, margen: 30 min (185 min de holgura requerida)

    Cálculo a mano:
        08:00 - 185 min = 04:55 del 2026-09-21, que cae ANTES del inicio (06:00).
        La parcela no alcanza a despacharse en este periodo con estos tiempos.

    Resultado esperado: VentanaInalcanzable.
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 8, 0),
    )
    with pytest.raises(VentanaInalcanzable):
        fecha_limite_corte(
            ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=30
        )
