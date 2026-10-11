"""Casos adicionales de estimación de insumos de empaque."""
from datetime import date

import pytest

from app.core.insumos.estimacion import estimar


def test_estimacion_tres_insumos_con_deficits_por_nombre():
    """Caso 06 — tres insumos, comprobados por nombre sin depender del orden.

    Entradas:
        volumen: 20; coeficientes: cajas 0.85, carton 0.85, bolsas 1.0;
        inventario: cajas 10, carton 5, bolsas 15.

    Cálculo a mano:
        cajas: requerida = 20 * 0.85 = 17.0; déficit = 17.0 - 10 = 7.0.
        carton: requerida = 20 * 0.85 = 17.0; déficit = 17.0 - 5 = 12.0.
        bolsas: requerida = 20 * 1.0 = 20.0; déficit = 20.0 - 15 = 5.0.

    Resultado esperado: requeridos 17.0/17.0/20.0 y déficits 7.0/12.0/5.0.
    """
    resultado = estimar(
        volumen_racimos=20,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85, "carton": 0.85, "bolsas": 1.0},
        inventario={"cajas": 10, "carton": 5, "bolsas": 15},
    )
    por_insumo = {item.insumo: item for item in resultado}

    assert por_insumo["cajas"].cantidad_requerida == pytest.approx(17.0)
    assert por_insumo["cajas"].deficit == pytest.approx(7.0)
    assert por_insumo["carton"].cantidad_requerida == pytest.approx(17.0)
    assert por_insumo["carton"].deficit == pytest.approx(12.0)
    assert por_insumo["bolsas"].cantidad_requerida == pytest.approx(20.0)
    assert por_insumo["bolsas"].deficit == pytest.approx(5.0)


def test_estimacion_inventario_igual_al_requerido_da_deficit_cero():
    """Caso 06b — inventario igual a la cantidad requerida.

    Entradas:
        volumen: 20; coeficiente cajas: 0.85; inventario cajas: 17.

    Cálculo a mano:
        requerida = 20 * 0.85 = 17.0.
        déficit = max(0, 17.0 - 17) = 0.0.

    Resultado esperado: requerida 17.0 y déficit 0.0.
    """
    resultado = estimar(
        volumen_racimos=20,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 17},
    )
    por_insumo = {item.insumo: item for item in resultado}

    assert por_insumo["cajas"].cantidad_requerida == pytest.approx(17.0)
    assert por_insumo["cajas"].deficit == pytest.approx(0.0)


def test_estimacion_inventario_vacio_cubre_deficit_total():
    """Caso 06c — inventario vacío para cajas.

    Entradas:
        volumen: 10; coeficiente cajas: 0.85; inventario: vacío.

    Cálculo a mano:
        requerida = 10 * 0.85 = 8.5.
        déficit = max(0, 8.5 - 0) = 8.5.

    Resultado esperado: requerida 8.5 y déficit 8.5.
    """
    resultado = estimar(
        volumen_racimos=10,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={},
    )
    por_insumo = {item.insumo: item for item in resultado}

    assert por_insumo["cajas"].cantidad_requerida == pytest.approx(8.5)
    assert por_insumo["cajas"].deficit == pytest.approx(8.5)


def test_estimacion_volumen_cero_da_requerido_y_deficit_cero():
    """Caso 06d — volumen de cosecha igual a cero.

    Entradas:
        volumen: 0; coeficiente cajas: 0.85; inventario cajas: 10.

    Cálculo a mano:
        requerida = 0 * 0.85 = 0.0.
        déficit = max(0, 0.0 - 10) = 0.0.

    Resultado esperado: requerida 0.0 y déficit 0.0.
    """
    resultado = estimar(
        volumen_racimos=0,
        fecha=date(2026, 9, 21),
        coeficientes={"cajas": 0.85},
        inventario={"cajas": 10},
    )
    por_insumo = {item.insumo: item for item in resultado}

    assert por_insumo["cajas"].cantidad_requerida == pytest.approx(0.0)
    assert por_insumo["cajas"].deficit == pytest.approx(0.0)


def test_estimacion_rechaza_volumen_negativo():
    """Caso 06e — volumen de racimos negativo.

    Entradas:
        volumen: -1; coeficiente cajas: 0.85; inventario cajas: 0.

    Cálculo a mano:
        -1 racimos no representa un volumen de cosecha válido; no hay requerimiento
        ni déficit calculables.

    Resultado esperado: ValueError.
    """
    with pytest.raises(ValueError):
        estimar(
            volumen_racimos=-1,
            fecha=date(2026, 9, 21),
            coeficientes={"cajas": 0.85},
            inventario={"cajas": 0},
        )
