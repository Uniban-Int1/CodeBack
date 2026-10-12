"""Pruebas técnicas del modelo predictivo con datos sintéticos."""
import numpy as np
import pandas as pd
import pytest

from app.core.proyeccion.predictivo import ModeloEntrenado, entrenar, predecir


@pytest.fixture
def observaciones_sinteticas():
    return pd.DataFrame(
        {
            "caracteristica_sintetica_a": [1.0, 2.0, 3.0, 4.0],
            "caracteristica_sintetica_b": [2.0, 1.0, 3.0, 0.0],
            "objetivo_sintetico": [8.0, 7.0, 15.0, 8.0],
        }
    )


@pytest.fixture
def modelo_sintetico(observaciones_sinteticas):
    return entrenar(
        observaciones_sinteticas,
        columnas_predictoras=(
            "caracteristica_sintetica_a",
            "caracteristica_sintetica_b",
        ),
        columna_objetivo="objetivo_sintetico",
    )


def test_entrenar_crea_modelo_y_conserva_caracteristicas_en_orden_sintetico(
    modelo_sintetico,
):
    assert isinstance(modelo_sintetico, ModeloEntrenado)
    assert modelo_sintetico.columnas_predictoras == (
        "caracteristica_sintetica_a",
        "caracteristica_sintetica_b",
    )
    assert modelo_sintetico.columna_objetivo == "objetivo_sintetico"


def test_predecir_devuelve_predicciones_para_dataframe_sintetico(
    observaciones_sinteticas, modelo_sintetico
):
    X_sintetico = observaciones_sinteticas[
        ["caracteristica_sintetica_a", "caracteristica_sintetica_b"]
    ]

    predicciones = predecir(modelo_sintetico, X_sintetico)

    assert isinstance(predicciones, np.ndarray)
    assert predicciones.shape == (4,)
    assert predicciones == pytest.approx([8.0, 7.0, 15.0, 8.0])


def test_predecir_respeta_orden_entrenado_y_ignora_columnas_adicionales(
    modelo_sintetico, observaciones_sinteticas
):
    X_sintetico = observaciones_sinteticas[
        ["caracteristica_sintetica_a", "caracteristica_sintetica_b"]
    ]
    X_sintetico_reordenado = pd.DataFrame(
        {
            "extra_sintetica": [100.0, 200.0, 300.0, 400.0],
            "caracteristica_sintetica_b": X_sintetico[
                "caracteristica_sintetica_b"
            ],
            "caracteristica_sintetica_a": X_sintetico[
                "caracteristica_sintetica_a"
            ],
        }
    )

    predicciones = predecir(modelo_sintetico, X_sintetico_reordenado)
    predicciones_orden_original = predecir(modelo_sintetico, X_sintetico)

    assert predicciones == pytest.approx(predicciones_orden_original)


@pytest.mark.parametrize(
    "observaciones_invalidas",
    [
        pd.DataFrame(
            columns=[
                "caracteristica_sintetica",
                "objetivo_sintetico",
            ]
        ),
        pd.DataFrame(
            {
                "caracteristica_sintetica": [1.0],
            }
        ),
        pd.DataFrame(
            {
                "objetivo_sintetico": [1.0],
            }
        ),
    ],
)
def test_entrenar_rechaza_dataframe_vacio_o_columnas_ausentes(
    observaciones_invalidas,
):
    with pytest.raises(ValueError):
        entrenar(
            observaciones_invalidas,
            columnas_predictoras=("caracteristica_sintetica",),
            columna_objetivo="objetivo_sintetico",
        )


@pytest.mark.parametrize(
    ("columna", "valor_invalido"),
    [
        ("caracteristica_sintetica", None),
        ("caracteristica_sintetica", "no-numerico"),
        ("caracteristica_sintetica", float("inf")),
        ("objetivo_sintetico", np.nan),
        ("objetivo_sintetico", "no-numerico"),
        ("objetivo_sintetico", float("-inf")),
    ],
)
def test_entrenar_rechaza_valores_invalidos_en_caracteristicas_y_objetivo(
    columna, valor_invalido
):
    observaciones_sinteticas_invalidas = pd.DataFrame(
        {
            "caracteristica_sintetica": [1.0, 2.0],
            "objetivo_sintetico": [2.0, 4.0],
        }
    )
    observaciones_sinteticas_invalidas[columna] = observaciones_sinteticas_invalidas[
        columna
    ].astype(object)
    observaciones_sinteticas_invalidas.loc[0, columna] = valor_invalido

    with pytest.raises(ValueError):
        entrenar(
            observaciones_sinteticas_invalidas,
            columnas_predictoras=("caracteristica_sintetica",),
            columna_objetivo="objetivo_sintetico",
        )


def test_entrenar_rechaza_claves_parcela_periodo_duplicadas_sinteticas():
    observaciones_sinteticas_duplicadas = pd.DataFrame(
        {
            "parcela_id": ["P-001", "P-001"],
            "periodo": ["2026-W38", "2026-W38"],
            "caracteristica_sintetica": [1.0, 2.0],
            "objetivo_sintetico": [2.0, 4.0],
        }
    )

    with pytest.raises(ValueError, match="debe ser única"):
        entrenar(
            observaciones_sinteticas_duplicadas,
            columnas_predictoras=("caracteristica_sintetica",),
            columna_objetivo="objetivo_sintetico",
        )


def test_entrenar_no_exige_claves_temporales_si_no_vienen_en_dataframe():
    observaciones_sinteticas = pd.DataFrame(
        {
            "caracteristica_sintetica": [1.0, 2.0],
            "objetivo_sintetico": [2.0, 4.0],
        }
    )

    modelo = entrenar(
        observaciones_sinteticas,
        columnas_predictoras=("caracteristica_sintetica",),
        columna_objetivo="objetivo_sintetico",
    )

    assert isinstance(modelo, ModeloEntrenado)


def test_predecir_rechaza_caracteristicas_distintas_a_las_del_entrenamiento(
    modelo_sintetico,
):
    X_sintetico_incompatible = pd.DataFrame(
        {"caracteristica_sintetica_a": [1.0]}
    )

    with pytest.raises(ValueError, match="caracteristica_sintetica_b"):
        predecir(modelo_sintetico, X_sintetico_incompatible)


@pytest.mark.parametrize(
    "X_sintetico_invalido",
    [
        pd.DataFrame(
            columns=[
                "caracteristica_sintetica_a",
                "caracteristica_sintetica_b",
            ]
        ),
        pd.DataFrame(
            {
                "caracteristica_sintetica_a": [1.0],
            }
        ),
    ],
)
def test_predecir_rechaza_dataframe_vacio_o_caracteristicas_ausentes(
    modelo_sintetico, X_sintetico_invalido
):
    with pytest.raises(ValueError):
        predecir(modelo_sintetico, X_sintetico_invalido)


@pytest.mark.parametrize(
    ("columna", "valor_invalido"),
    [
        ("caracteristica_sintetica_a", None),
        ("caracteristica_sintetica_a", "no-numerico"),
        ("caracteristica_sintetica_a", float("nan")),
        ("caracteristica_sintetica_a", float("-inf")),
        ("caracteristica_sintetica_b", None),
        ("caracteristica_sintetica_b", "no-numerico"),
        ("caracteristica_sintetica_b", float("nan")),
        ("caracteristica_sintetica_b", float("-inf")),
    ],
)
def test_predecir_rechaza_caracteristicas_invalidas(
    modelo_sintetico, columna, valor_invalido
):
    X_sintetico_invalido = pd.DataFrame(
        {
            "caracteristica_sintetica_a": [1.0],
            "caracteristica_sintetica_b": [1.0],
        }
    )
    X_sintetico_invalido[columna] = X_sintetico_invalido[columna].astype(object)
    X_sintetico_invalido.loc[0, columna] = valor_invalido

    with pytest.raises(ValueError):
        predecir(modelo_sintetico, X_sintetico_invalido)


def test_predecir_rechaza_claves_parcela_periodo_duplicadas_sinteticas(
    modelo_sintetico,
):
    X_sintetico_duplicado = pd.DataFrame(
        {
            "parcela_id": ["P-001", "P-001"],
            "periodo": ["2026-W38", "2026-W38"],
            "caracteristica_sintetica_a": [1.0, 2.0],
            "caracteristica_sintetica_b": [2.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="debe ser única"):
        predecir(modelo_sintetico, X_sintetico_duplicado)
