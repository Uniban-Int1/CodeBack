"""Métricas predictivas: pruebas técnicas con datos sintéticos."""
import pandas as pd
import pytest

from app.core.proyeccion.metricas import comparar, mae


def test_mae_calcula_error_absoluto_medio_con_datos_sinteticos():
    y_real_sintetico = [10.0, 20.0, 30.0]
    y_pred_sintetico = [12.0, 18.0, 33.0]

    assert mae(y_real_sintetico, y_pred_sintetico) == pytest.approx(7 / 3)


def test_mae_rechaza_longitudes_incompatibles():
    with pytest.raises(ValueError, match="misma longitud"):
        mae([1.0, 2.0], [1.0])


@pytest.mark.parametrize(
    ("y_real_sintetico", "y_pred_sintetico"),
    [
        ([], []),
        ([1.0], [float("nan")]),
        ([float("inf")], [1.0]),
        ([True], [1.0]),
        (["1.0"], [1.0]),
    ],
)
def test_mae_rechaza_entrada_vacia_o_valores_no_validos(
    y_real_sintetico, y_pred_sintetico
):
    with pytest.raises(ValueError):
        mae(y_real_sintetico, y_pred_sintetico)


def test_comparar_alinea_mae_en_las_mismas_observaciones_sinteticas():
    observaciones_sinteticas = pd.DataFrame(
        [
            {
                "parcela_id": "P-001",
                "periodo": "2026-W38",
                "y_real": 10.0,
                "y_pred_modelo": 11.0,
                "y_pred_base": 8.0,
                "y_pred_ingenua": 9.0,
            },
            {
                "parcela_id": "P-002",
                "periodo": "2026-W38",
                "y_real": 20.0,
                "y_pred_modelo": 18.0,
                "y_pred_base": 20.0,
                "y_pred_ingenua": 25.0,
            },
            {
                "parcela_id": "P-001",
                "periodo": "2026-W39",
                "y_real": 30.0,
                "y_pred_modelo": 33.0,
                "y_pred_base": 27.0,
                "y_pred_ingenua": 29.0,
            },
        ]
    )

    resultado = comparar(observaciones_sinteticas)

    assert resultado.periodos == ("2026-W38", "2026-W39")
    assert resultado.n_observaciones == 3
    assert resultado.mae_predictivo == pytest.approx(2.0)
    assert resultado.mae_determinista == pytest.approx(5 / 3)
    assert resultado.mae_ingenua == pytest.approx(7 / 3)


def test_comparar_rechaza_claves_parcela_periodo_duplicadas():
    observaciones_sinteticas = pd.DataFrame(
        [
            {
                "parcela_id": "P-001",
                "periodo": "2026-W38",
                "y_real": 10.0,
                "y_pred_modelo": 11.0,
                "y_pred_base": 9.0,
                "y_pred_ingenua": 9.5,
            },
            {
                "parcela_id": "P-001",
                "periodo": "2026-W38",
                "y_real": 10.0,
                "y_pred_modelo": 12.0,
                "y_pred_base": 8.0,
                "y_pred_ingenua": 9.0,
            },
        ]
    )

    with pytest.raises(ValueError, match="debe ser única"):
        comparar(observaciones_sinteticas)


def test_comparar_rechaza_dataframe_vacio():
    observaciones_sinteticas_vacias = pd.DataFrame(
        columns=[
            "parcela_id",
            "periodo",
            "y_real",
            "y_pred_modelo",
            "y_pred_base",
            "y_pred_ingenua",
        ]
    )

    with pytest.raises(ValueError, match="observaciones no puede estar vacío"):
        comparar(observaciones_sinteticas_vacias)


@pytest.mark.parametrize(
    ("columna", "valor_invalido"),
    [
        ("y_real", float("nan")),
        ("y_real", "volumen-desconocido"),
    ],
)
def test_comparar_rechaza_valor_real_invalido(columna, valor_invalido):
    fila_sintetica = {
        "parcela_id": "P-001",
        "periodo": "2026-W38",
        "y_real": 10.0,
        "y_pred_modelo": 11.0,
        "y_pred_base": 9.0,
        "y_pred_ingenua": 9.5,
    }
    fila_sintetica[columna] = valor_invalido
    observaciones_sinteticas = pd.DataFrame([fila_sintetica])

    with pytest.raises(ValueError, match="solo números finitos"):
        comparar(observaciones_sinteticas)


@pytest.mark.parametrize(
    ("columna", "valor_invalido"),
    [
        ("y_pred_modelo", "prediccion-desconocida"),
        ("y_pred_base", "prediccion-desconocida"),
        ("y_pred_ingenua", "prediccion-desconocida"),
    ],
)
def test_comparar_rechaza_prediccion_no_numerica(columna, valor_invalido):
    fila_sintetica = {
        "parcela_id": "P-001",
        "periodo": "2026-W38",
        "y_real": 10.0,
        "y_pred_modelo": 11.0,
        "y_pred_base": 9.0,
        "y_pred_ingenua": 9.5,
    }
    fila_sintetica[columna] = valor_invalido
    observaciones_sinteticas = pd.DataFrame([fila_sintetica])

    with pytest.raises(ValueError, match="solo números finitos"):
        comparar(observaciones_sinteticas)


@pytest.mark.parametrize(
    ("columna", "valor_no_finito"),
    [
        ("y_pred_modelo", float("nan")),
        ("y_pred_base", float("inf")),
        ("y_pred_ingenua", float("-inf")),
    ],
)
def test_comparar_rechaza_prediccion_no_finita(columna, valor_no_finito):
    fila_sintetica = {
        "parcela_id": "P-001",
        "periodo": "2026-W38",
        "y_real": 10.0,
        "y_pred_modelo": 11.0,
        "y_pred_base": 9.0,
        "y_pred_ingenua": 9.5,
    }
    fila_sintetica[columna] = valor_no_finito
    observaciones_sinteticas = pd.DataFrame([fila_sintetica])

    with pytest.raises(ValueError, match="solo números finitos"):
        comparar(observaciones_sinteticas)
