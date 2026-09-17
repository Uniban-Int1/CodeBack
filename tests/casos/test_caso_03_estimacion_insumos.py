"""Caso 03 — derivación de insumos de empaque, situación normal.

Usa el mismo ejemplo publicado en docs/contrato-integracion.md para que el resultado
sea consistente entre lo que promete el contrato y lo que calcula el código.

Entradas:
    volumen_racimos: 484.7
    coeficiente cajas: 0.85 (racimos -> cajas)
    inventario cajas: 300

Cálculo a mano:
    cantidad_requerida = 484.7 * 0.85 = 411.995  ->  redondeado a 2 decimales: 412.0
    deficit = 412.0 - 300 = 112.0

Resultado esperado: cantidad_requerida=412.0, deficit=112.0
"""
from datetime import date

from app.core.insumos.estimacion import estimar


def test_estimacion_situacion_normal():
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
