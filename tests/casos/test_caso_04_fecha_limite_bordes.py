"""Casos adicionales de fecha límite de corte."""
from datetime import datetime

from app.core.programacion.fechas import VentanaDespacho, fecha_limite_corte


def test_fecha_limite_sin_margen_seguridad():
    """Caso 04 — ventana 2026-09-21 06:00 a 16:00 sin margen de seguridad.

    Entradas:
        ventana: 2026-09-21 06:00 a 16:00
        empaque: 120 min, acarreo: 35 min, margen: 0 min.

    Cálculo a mano:
        holgura total = 120 + 35 + 0 = 155 min = 2 h 35 min.
        16:00 - 2 h 35 min = 13:25 del 2026-09-21.

    Resultado esperado: 2026-09-21 13:25.
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )

    resultado = fecha_limite_corte(
        ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=0
    )

    assert resultado == datetime(2026, 9, 21, 13, 25)


def test_fecha_limite_acepta_holgura_igual_a_ventana():
    """Caso 04b — el borde exacto de una ventana de 600 minutos.

    Entradas:
        ventana: 2026-09-21 06:00 a 16:00 (600 min)
        empaque: 300 min, acarreo: 200 min, margen: 100 min.

    Cálculo a mano:
        holgura total = 300 + 200 + 100 = 600 min = 10 h.
        16:00 - 10 h = 06:00 del 2026-09-21, exactamente el inicio de la ventana.

    Resultado esperado: 2026-09-21 06:00; no debe lanzar VentanaInalcanzable.
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )

    resultado = fecha_limite_corte(
        ventana, minutos_empaque=300, minutos_acarreo=200, margen_seguridad_min=100
    )

    assert resultado == datetime(2026, 9, 21, 6, 0)
