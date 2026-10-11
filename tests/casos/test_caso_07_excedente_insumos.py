"""Casos de excedente explícito y validación de inventario."""
from datetime import date

import pytest

from app.core.insumos.estimacion import estimar


def test_estimacion_reporta_excedente_con_inventario_mayor_al_requerido():
    """Caso 07 — inventario mayor que el requerimiento de cajas.

    Entradas:
        volumen: 20; coeficiente cajas: 0.85; inventario cajas: 30.

    Cálculo a mano:
        requerida = 20 * 0.85 = 17.0.
        déficit = max(0, 17.0 - 30) = 0.0.
        excedente = max(0, 30 - 17.0) = 13.0.

    Resultado esperado: requerida 17.0, déficit 0.0 y excedente 13.0.
    """
    resultado = estimar(
        volumen_racimos=20,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 30},
    )
    item = resultado[0]

    assert item.cantidad_requerida == pytest.approx(17.0)
    assert item.deficit == pytest.approx(0.0)
    assert item.excedente == pytest.approx(13.0)


def test_estimacion_no_reporta_excedente_con_inventario_menor_al_requerido():
    """Caso 07b — inventario menor que el requerimiento de cajas.

    Entradas:
        volumen: 20; coeficiente cajas: 0.85; inventario cajas: 10.

    Cálculo a mano:
        requerida = 20 * 0.85 = 17.0.
        déficit = max(0, 17.0 - 10) = 7.0.
        excedente = max(0, 10 - 17.0) = 0.0.

    Resultado esperado: requerida 17.0, déficit 7.0 y excedente 0.0.
    """
    resultado = estimar(
        volumen_racimos=20,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 10},
    )
    item = resultado[0]

    assert item.cantidad_requerida == pytest.approx(17.0)
    assert item.deficit == pytest.approx(7.0)
    assert item.excedente == pytest.approx(0.0)


def test_estimacion_no_reporta_deficit_ni_excedente_con_inventario_igual():
    """Caso 07c — inventario igual al requerimiento de cajas.

    Entradas:
        volumen: 20; coeficiente cajas: 0.85; inventario cajas: 17.

    Cálculo a mano:
        requerida = 20 * 0.85 = 17.0.
        déficit = max(0, 17.0 - 17) = 0.0.
        excedente = max(0, 17 - 17.0) = 0.0.

    Resultado esperado: requerida 17.0, déficit 0.0 y excedente 0.0.
    """
    resultado = estimar(
        volumen_racimos=20,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 17},
    )
    item = resultado[0]

    assert item.cantidad_requerida == pytest.approx(17.0)
    assert item.deficit == pytest.approx(0.0)
    assert item.excedente == pytest.approx(0.0)


def test_estimacion_rechaza_inventario_negativo():
    """Caso 07d — inventario negativo de cajas.

    Entradas:
        volumen: 20; coeficiente cajas: 0.85; inventario cajas: -1.

    Cálculo a mano:
        requerida sería 20 * 0.85 = 17.0, pero -1 no es un inventario válido;
        no se calculan déficit ni excedente.

    Resultado esperado: ValueError que identifica el insumo cajas.
    """
    with pytest.raises(ValueError, match="cajas"):
        estimar(
            volumen_racimos=20,
            fecha=date(2026, 9, 21),
            coeficientes={"cajas": 0.85},
            inventario={"cajas": -1},
        )
