"""Casos de cálculo manual de fecha límite de corte."""
from datetime import datetime

import pytest

from app.core.programacion.fechas import (
    VentanaDespacho,
    VentanaInalcanzable,
    fecha_limite_corte,
)


def test_fecha_limite_situacion_normal():
    """T-09 01 — fecha límite para un escenario sintético normal.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        sintetico_ventana: 2026-09-21 06:00 a 16:00
        sintetico_minutos_empaque: 120
        sintetico_minutos_acarreo: 35
        sintetico_margen_seguridad_min: 30

    Cálculo manual:
        holgura = 120 + 35 + 30 = 185 minutos = 3 horas y 5 minutos.
        límite = 16:00 - 3 horas y 5 minutos = 12:55 del 2026-09-21.

    Resultado esperado: 2026-09-21 12:55.
    Justificación: se resta la holgura total a la hora de cierre de la ventana.
    """
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
    """T-09 02 — holgura que excede una ventana sintética.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        sintetico_ventana: 2026-09-21 06:00 a 08:00
        sintetico_minutos_empaque: 120
        sintetico_minutos_acarreo: 35
        sintetico_margen_seguridad_min: 30

    Cálculo manual:
        holgura = 120 + 35 + 30 = 185 minutos.
        límite teórico = 08:00 - 185 minutos = 04:55.
        04:55 es anterior al inicio de la ventana, 06:00.

    Resultado esperado: VentanaInalcanzable.
    Justificación: la función rechaza un límite calculado anterior al inicio de la ventana.
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 8, 0),
    )
    with pytest.raises(VentanaInalcanzable):
        fecha_limite_corte(
            ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=30
        )
