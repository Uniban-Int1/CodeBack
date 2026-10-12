"""Pruebas sintéticas de la métrica T-18; no son datos de Unibán."""
import pytest

from app.core.insumos.metricas import (
    ConsumoObservado,
    EstimacionInsumo,
    evaluar_error_absoluto,
)


UNIDAD_SINTETICA = "unidad_sintetica"


def estimacion(
    *,
    insumo="insumo_sintetico",
    parcela_id="P-SINTETICA",
    periodo="2026-W38",
    cantidad=10.0,
    unidad=UNIDAD_SINTETICA,
):
    return EstimacionInsumo(insumo, parcela_id, periodo, cantidad, unidad)


def consumo(
    *,
    insumo="insumo_sintetico",
    parcela_id="P-SINTETICA",
    periodo="2026-W38",
    cantidad=7.0,
    unidad=UNIDAD_SINTETICA,
):
    return ConsumoObservado(insumo, parcela_id, periodo, cantidad, unidad)


def assert_counts_match_records(resultado):
    assert resultado.n_evaluables == sum(
        registro.estado == "evaluable" for registro in resultado.registros
    )
    assert resultado.n_no_evaluables_consumo_ausente == sum(
        registro.estado == "consumo_ausente" for registro in resultado.registros
    )
    assert resultado.n_no_comparables == sum(
        registro.estado == "no_comparable" for registro in resultado.registros
    )


def test_error_absoluto_compara_claves_y_unidades_sinteticas_iguales():
    resultado = evaluar_error_absoluto([estimacion()], [consumo()])

    assert resultado.n_evaluables == 1
    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 0
    registro = resultado.registros[0]
    assert registro.estado == "evaluable"
    assert registro.error_absoluto == 3.0
    assert registro.insumo == "insumo_sintetico"
    assert registro.parcela_id == "P-SINTETICA"
    assert registro.periodo == "2026-W38"
    assert registro.unidad_requerida == UNIDAD_SINTETICA
    assert registro.unidad_observada == UNIDAD_SINTETICA
    assert_counts_match_records(resultado)


def test_error_absoluto_acepta_consumo_observado_cero_sintetico():
    resultado = evaluar_error_absoluto(
        [estimacion()], [consumo(cantidad=0.0)]
    )

    assert resultado.n_evaluables == 1
    assert resultado.registros[0].cantidad_observada == 0.0
    assert resultado.registros[0].error_absoluto == 10.0
    assert_counts_match_records(resultado)


def test_consumo_sintetico_ausente_no_se_reemplaza_por_cero():
    resultado = evaluar_error_absoluto(
        [estimacion()], [consumo(cantidad=None)]
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 1
    assert resultado.n_no_comparables == 0
    registro = resultado.registros[0]
    assert registro.estado == "consumo_ausente"
    assert registro.cantidad_observada is None
    assert registro.error_absoluto is None
    assert_counts_match_records(resultado)


def test_sin_registro_de_consumo_es_ausencia_real():
    resultado = evaluar_error_absoluto([estimacion()], [])

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 1
    assert resultado.n_no_comparables == 0
    assert len(resultado.registros) == 1
    assert resultado.registros[0].lado == "estimacion"
    assert resultado.registros[0].estado == "consumo_ausente"
    assert resultado.registros[0].error_absoluto is None
    assert_counts_match_records(resultado)


@pytest.mark.parametrize(
    "estimacion_sintetica",
    [
        estimacion(insumo=None),
        estimacion(parcela_id=""),
        estimacion(periodo="2026-W54"),
    ],
)
def test_claves_incompletas_o_periodo_invalido_son_no_comparables(
    estimacion_sintetica,
):
    resultado = evaluar_error_absoluto(
        [estimacion_sintetica], [consumo()]
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_comparables == 2
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert_counts_match_records(resultado)


def test_estimacion_con_periodo_invalido_reporta_consumo_potencial():
    resultado = evaluar_error_absoluto(
        [estimacion(periodo="2026-W54")],
        [consumo(periodo="2026-W38")],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 2
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "consumo",
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert "periodo ISO inválido" in resultado.registros[0].motivo
    assert "periodo inválido" in resultado.registros[1].motivo
    assert_counts_match_records(resultado)


def test_estimacion_con_clave_incompleta_reporta_consumo_potencial():
    resultado = evaluar_error_absoluto(
        [estimacion(parcela_id=None)],
        [consumo()],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 2
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "consumo",
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert "claves incompletas" in resultado.registros[0].motivo
    assert "claves incompletas" in resultado.registros[1].motivo
    assert_counts_match_records(resultado)


def test_periodo_de_consumo_invalido_no_se_clasifica_como_ausente():
    resultado = evaluar_error_absoluto(
        [estimacion()],
        [consumo(periodo="2026-W54")],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 2
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "consumo",
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert "periodo inválido" in resultado.registros[0].motivo
    assert_counts_match_records(resultado)


def test_consumo_con_periodo_invalido_no_se_asigna_a_estimaciones_potenciales():
    resultado = evaluar_error_absoluto(
        [
            estimacion(periodo="2026-W38", cantidad=10.0),
            estimacion(periodo="2026-W39", cantidad=11.0),
        ],
        [consumo(periodo="2026-W54")],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 3
    assert len(resultado.registros) == 3
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "estimacion",
        "consumo",
    ]
    assert [registro.periodo for registro in resultado.registros] == [
        "2026-W38",
        "2026-W39",
        "2026-W54",
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert all(
        "periodo inválido" in registro.motivo
        for registro in resultado.registros[:2]
    )
    assert "periodo ISO inválido" in resultado.registros[2].motivo
    assert [registro.cantidad_requerida for registro in resultado.registros] == [
        10.0,
        11.0,
        None,
    ]
    assert_counts_match_records(resultado)


def test_periodo_sintetico_sin_coincidencia_es_no_comparable():
    resultado = evaluar_error_absoluto(
        [estimacion(periodo="2026-W38")],
        [consumo(periodo="2026-W39")],
    )

    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 2
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert_counts_match_records(resultado)


def test_unidades_sinteticas_incompatibles_son_no_comparables():
    resultado = evaluar_error_absoluto(
        [estimacion(unidad="unidad_sintetica_a")],
        [consumo(unidad="unidad_sintetica_b")],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_comparables == 1
    assert resultado.registros[0].error_absoluto is None


def test_consumos_sinteticos_duplicados_no_se_emparejan_arbitrariamente():
    resultado = evaluar_error_absoluto(
        [estimacion()],
        [consumo(cantidad=7.0), consumo(cantidad=8.0)],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_comparables == 3
    assert len(resultado.registros) == 3
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "consumo",
        "consumo",
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert [registro.cantidad_observada for registro in resultado.registros] == [
        None,
        7.0,
        8.0,
    ]
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert_counts_match_records(resultado)


def test_estimaciones_sinteticas_duplicadas_no_se_emparejan_arbitrariamente():
    resultado = evaluar_error_absoluto(
        [estimacion(cantidad=10.0), estimacion(cantidad=11.0)],
        [consumo()],
    )

    assert resultado.n_evaluables == 0
    assert resultado.n_no_comparables == 3
    assert len(resultado.registros) == 3
    assert [registro.lado for registro in resultado.registros] == [
        "estimacion",
        "estimacion",
        "consumo",
    ]
    assert [registro.cantidad_requerida for registro in resultado.registros] == [
        10.0,
        11.0,
        None,
    ]
    assert all(registro.estado == "no_comparable" for registro in resultado.registros)
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert_counts_match_records(resultado)


def test_consumo_sintetico_con_clave_incompleta_se_reporta_no_comparable():
    resultado = evaluar_error_absoluto(
        [estimacion()],
        [consumo(parcela_id=None)],
    )

    assert resultado.n_no_evaluables_consumo_ausente == 0
    assert resultado.n_no_comparables == 2
    assert all(registro.error_absoluto is None for registro in resultado.registros)
    assert resultado.registros[1].lado == "consumo"
    assert resultado.registros[1].estado == "no_comparable"
    assert_counts_match_records(resultado)


def test_no_agrega_errores_de_unidades_sinteticas_diferentes():
    resultado = evaluar_error_absoluto(
        [
            estimacion(insumo="insumo_a", unidad="unidad_sintetica_a"),
            estimacion(insumo="insumo_b", unidad="unidad_sintetica_b"),
        ],
        [
            consumo(insumo="insumo_a", cantidad=7.0, unidad="unidad_sintetica_a"),
            consumo(insumo="insumo_b", cantidad=6.0, unidad="unidad_sintetica_b"),
        ],
    )

    assert resultado.n_evaluables == 2
    assert [registro.error_absoluto for registro in resultado.registros] == [3.0, 4.0]
    assert_counts_match_records(resultado)
