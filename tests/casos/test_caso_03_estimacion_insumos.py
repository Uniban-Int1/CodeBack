"""Casos de cálculo manual de estimación de insumos."""
from datetime import date

from app.core.insumos.estimacion import estimar


def test_estimacion_situacion_normal():
    """T-09 06 — requerimiento de cajas para entradas sintéticas.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        sintetico_volumen_racimos: 484.7
        sintetico_coeficiente_cajas: 0.85
        sintetico_inventario_cajas: 300
        sintetico_fecha: 2026-09-20

    Cálculo manual:
        cantidad requerida = 484.7 × 0.85 = 411.995.
        redondeada a dos decimales por estimar = 412.0.
        déficit = max(0, 412.0 - 300) = 112.0.

    Resultado esperado: requerido 412.0; inventario 300; déficit 112.0.
    Justificación: el déficit es la diferencia positiva entre el requerido redondeado y el inventario.
    """
    resultado = estimar(
        volumen_racimos=484.7,
        fecha=date(2026, 9, 20),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 300},
    )
    assert len(resultado) == 1
    item = resultado[0]
    assert item.insumo == "cajas"
    assert item.cantidad_requerida == 412.0
    assert item.inventario_disponible == 300
    assert item.deficit == 112.0


def test_estimacion_inventario_suficiente_no_genera_deficit():
    """Caso 03b — el inventario alcanza: el déficit es 0, nunca negativo."""
    resultado = estimar(
        volumen_racimos=100,
        fecha=date(2026, 9, 20),
        coeficientes={"bolsas": 1.0},
        inventario={"bolsas": 500},
    )
    assert resultado[0].cantidad_requerida == 100.0
    assert resultado[0].deficit == 0.0
