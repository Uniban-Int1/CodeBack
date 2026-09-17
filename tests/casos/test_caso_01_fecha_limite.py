"""Caso 01 — fecha límite de corte, situación normal.

Entradas:
    ventana de despacho: 2026-09-21 06:00 a 16:00
    tiempo de empaque:   120 min
    tiempo de acarreo:    35 min
    margen de seguridad:  30 min

Cálculo a mano:
    16:00 - 120 min - 35 min - 30 min = 13:55 del 2026-09-21

Resultado esperado: 2026-09-21 13:55
"""
import pytest

from app.core.programacion.fechas import VentanaDespacho, fecha_limite_corte
from datetime import datetime


@pytest.mark.xfail(reason="T-07 sin implementar")
def test_fecha_limite_situacion_normal():
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )
    resultado = fecha_limite_corte(
        ventana, minutos_empaque=120, minutos_acarreo=35, margen_seguridad_min=30
    )
    assert resultado == datetime(2026, 9, 21, 13, 55)
