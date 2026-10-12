"""Casos de cálculo manual de proyección determinista."""
from app.core.proyeccion.base import Aforamiento, proyectar


def test_proyeccion_situacion_normal():
    """T-09 04 — proyección determinista con entradas sintéticas.

    Escenario sintético; estos valores no son datos históricos de Unibán.

    Entradas:
        sintetico_num_plantas: 1850
        sintetico_area_ha: 2.4
        sintetico_calidad_confianza: 0.87
        sintetico_ciclo_racimo_semanas: 10.5
        sintetico_factor_perdida: 0.05
        sintetico_periodo: 2026-W38
        sintetico_parcela_id: P-018

    Cálculo manual:
        tasa semanal = 1 / 10.5 = 0.0952380952...
        volumen = 1850 × (1 / 10.5) × 0.87 × (1 - 0.05)
                = 145.621428...
        redondeado a una decimal = 145.6.

    Resultado esperado: 145.6 racimos.
    Justificación: se aplica la fórmula de proyección y su redondeo a una decimal.
    """
    aforamiento = Aforamiento(
        parcela_id="P-018",
        num_plantas=1850,
        area_ha=2.4,
        calidad_confianza=0.87,
    )
    resultado = proyectar(
        aforamiento,
        periodo="2026-W38",
        ciclo_racimo_semanas=10.5,
        factor_perdida=0.05,
    )
    assert resultado.volumen_racimos == 145.6
    assert resultado.metodo == "determinista-v1"
    assert resultado.parcela_id == "P-018"
    assert resultado.periodo == "2026-W38"


def test_proyeccion_rechaza_confianza_fuera_de_rango():
    aforamiento = Aforamiento(
        parcela_id="P-018", num_plantas=1850, area_ha=2.4, calidad_confianza=1.4
    )
    try:
        proyectar(aforamiento, periodo="2026-W38", ciclo_racimo_semanas=10.5)
        assert False, "debía lanzar ValueError"
    except ValueError:
        pass
