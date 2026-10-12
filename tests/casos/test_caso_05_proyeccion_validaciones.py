"""Casos adicionales de proyección determinista de cosecha."""
import pytest

from app.core.proyeccion.base import Aforamiento, proyectar


def test_proyeccion_cero_plantas_da_cero():
    """T-09 05 — proyección con cero plantas en un escenario sintético.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        sintetico_num_plantas: 0
        sintetico_calidad_confianza: 1.0
        sintetico_area_ha: 1.0
        sintetico_ciclo_racimo_semanas: 5
        sintetico_factor_perdida: 0 (valor por defecto)
        sintetico_periodo: 2026-W38
        sintetico_parcela_id: P-000

    Cálculo manual:
        volumen = 0 × (1 / 5) × 1.0 × (1 - 0) = 0.0.

    Resultado esperado: 0.0 racimos.
    Justificación: el número de plantas es cero, por lo que el producto de la fórmula es cero.
    """
    aforamiento = Aforamiento("P-000", 0, 1.0, 1.0)

    resultado = proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=5)

    assert resultado.volumen_racimos == pytest.approx(0.0)


def test_proyeccion_confianza_cero_da_cero():
    """Caso 05b — confianza de aforamiento igual a cero.

    Entradas:
        num_plantas: 100, calidad_confianza: 0.0, ciclo: 5 semanas, pérdida: 0.

    Cálculo a mano:
        volumen = 100 * (1 / 5) * 0.0 * (1 - 0) = 0.0.

    Resultado esperado: 0.0 racimos.
    """
    aforamiento = Aforamiento("P-001", 100, 1.0, 0.0)

    resultado = proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=5)

    assert resultado.volumen_racimos == pytest.approx(0.0)


def test_proyeccion_sin_perdida_en_ciclo_de_cinco_semanas():
    """Caso 05c — proyección sin pérdidas.

    Entradas:
        num_plantas: 100, calidad_confianza: 1.0, ciclo: 5 semanas, pérdida: 0.

    Cálculo a mano:
        tasa semanal = 1 / 5 = 0.2.
        volumen = 100 * 0.2 * 1.0 * (1 - 0) = 20.0.

    Resultado esperado: 20.0 racimos.
    """
    aforamiento = Aforamiento("P-002", 100, 1.0, 1.0)

    resultado = proyectar(
        aforamiento, "2026-W38", ciclo_racimo_semanas=5, factor_perdida=0
    )

    assert resultado.volumen_racimos == pytest.approx(20.0)


def test_proyeccion_rechaza_numero_de_plantas_negativo():
    """Caso 05d — número de plantas negativo.

    Entradas:
        num_plantas: -1, calidad_confianza: 1.0, ciclo: 5 semanas, pérdida: 0.

    Cálculo a mano:
        -1 plantas no representa un aforamiento válido; no hay volumen calculable.

    Resultado esperado: ValueError.
    """
    aforamiento = Aforamiento("P-003", -1, 1.0, 1.0)

    with pytest.raises(ValueError):
        proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=5)


def test_proyeccion_rechaza_confianza_negativa():
    """Caso 05d bis — confianza de aforamiento negativa.

    Entradas:
        num_plantas: 100, calidad_confianza: -0.1, ciclo: 5 semanas, pérdida: 0.

    Resultado esperado: ValueError con el mensaje de validación del rango válido.
    """
    aforamiento = Aforamiento("P-003a", 100, 1.0, -0.1)

    with pytest.raises(ValueError, match=r"calidad_confianza debe estar en \[0, 1\]"):
        proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=5)


def test_proyeccion_rechaza_confianza_mayor_que_uno():
    """Caso 05d ter — confianza de aforamiento mayor que uno.

    Entradas:
        num_plantas: 100, calidad_confianza: 1.1, ciclo: 5 semanas, pérdida: 0.

    Resultado esperado: ValueError con el mensaje de validación del rango válido.
    """
    aforamiento = Aforamiento("P-003b", 100, 1.0, 1.1)

    with pytest.raises(ValueError, match=r"calidad_confianza debe estar en \[0, 1\]"):
        proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=5)


def test_proyeccion_rechaza_ciclo_cero():
    """Caso 05e — ciclo de racimo igual a cero semanas.

    Entradas:
        num_plantas: 100, calidad_confianza: 1.0, ciclo: 0 semanas, pérdida: 0.

    Cálculo a mano:
        la tasa semanal sería 1 / 0, una división sin valor definido; no hay volumen calculable.

    Resultado esperado: ValueError.
    """
    aforamiento = Aforamiento("P-004", 100, 1.0, 1.0)

    with pytest.raises(ValueError):
        proyectar(aforamiento, "2026-W38", ciclo_racimo_semanas=0)


def test_proyeccion_rechaza_factor_perdida_mayor_que_uno():
    """Caso 05f — factor de pérdida fuera de rango.

    Entradas:
        num_plantas: 100, calidad_confianza: 1.0, ciclo: 5 semanas, pérdida: 1.5.

    Cálculo a mano:
        1.5 equivale a 150 % de pérdida y está fuera del rango válido [0, 1];
        no hay volumen calculable.

    Resultado esperado: ValueError.
    """
    aforamiento = Aforamiento("P-005", 100, 1.0, 1.0)

    with pytest.raises(ValueError):
        proyectar(
            aforamiento, "2026-W38", ciclo_racimo_semanas=5, factor_perdida=1.5
        )
