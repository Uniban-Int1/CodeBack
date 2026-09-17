"""Caso 02 — proyección determinista de cosecha, situación normal.

Entradas:
    num_plantas:            1850
    calidad_confianza:      0.87
    ciclo_racimo_semanas:   10.5
    factor_perdida:         0.05

Cálculo a mano:
    tasa_semanal = 1 / 10.5 = 0.095238...
    volumen = 1850 * 0.095238... * 0.87 * (1 - 0.05)
            = 1850 * 0.095238... * 0.87 * 0.95
            = 145.5626...  ->  redondeado a 1 decimal: 145.6

Resultado esperado: 145.6 racimos
"""
from app.core.proyeccion.base import Aforamiento, proyectar


def test_proyeccion_situacion_normal():
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


def test_proyeccion_rechaza_confianza_fuera_de_rango():
    aforamiento = Aforamiento(
        parcela_id="P-018", num_plantas=1850, area_ha=2.4, calidad_confianza=1.4
    )
    try:
        proyectar(aforamiento, periodo="2026-W38", ciclo_racimo_semanas=10.5)
        assert False, "debía lanzar ValueError"
    except ValueError:
        pass
