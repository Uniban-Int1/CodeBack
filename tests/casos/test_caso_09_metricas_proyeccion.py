"""Métricas predictivas: pruebas técnicas con datos sintéticos."""
import pandas as pd
import pytest

from app.core.proyeccion.metricas import (
    comparar,
    comparar_metodos_disponibles,
    linea_base_ingenua,
    mae,
)


def _observaciones_reales_sinteticas(filas):
    return pd.DataFrame(filas, columns=["parcela_id", "periodo", "y_real"])


def _claves_pronostico_sinteticas(filas):
    return pd.DataFrame(filas, columns=["parcela_id", "periodo"])


def test_linea_base_ingenua_usa_la_semana_iso_anterior_sintetica():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2026-W37", 12.5)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W38")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [12.5]


def test_linea_base_ingenua_resuelve_cambio_de_anio_iso_sintetico():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2025-W52", 17.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W01")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [17.0]


def test_linea_base_ingenua_no_busca_semana_mas_antigua_si_falta_la_anterior():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2026-W35", 8.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W37")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [None]


def test_linea_base_ingenua_no_usa_observaciones_posteriores_sinteticas():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2026-W39", 25.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W38")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [None]


def test_linea_base_ingenua_conserva_cero_real_explicito_sintetico():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2026-W37", 0.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W38")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    prediccion = resultado.loc[0, "y_pred_ingenua"]
    assert prediccion == 0.0
    assert prediccion is not None


def test_linea_base_ingenua_devuelve_no_disponible_sin_historial_sintetico():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas([])
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W38")]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [None]


def test_linea_base_ingenua_mantiene_historiales_de_parcelas_independientes():
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [
            ("P-001", "2026-W37", 10.0),
            ("P-002", "2026-W37", 20.0),
        ]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [
            ("P-002", "2026-W38"),
            ("P-001", "2026-W38"),
        ]
    )

    resultado = linea_base_ingenua(
        observaciones_reales_sinteticas, claves_pronostico_sinteticas
    )

    assert resultado["y_pred_ingenua"].tolist() == [20.0, 10.0]


@pytest.mark.parametrize("duplicadas_en", ["observaciones", "objetivos"])
def test_linea_base_ingenua_rechaza_claves_duplicadas_sinteticas(duplicadas_en):
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", "2026-W37", 10.0), ("P-001", "2026-W37", 12.0)]
        if duplicadas_en == "observaciones"
        else [("P-001", "2026-W37", 10.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", "2026-W38"), ("P-001", "2026-W38")]
        if duplicadas_en == "objetivos"
        else [("P-001", "2026-W38")]
    )

    with pytest.raises(ValueError, match="debe ser única"):
        linea_base_ingenua(
            observaciones_reales_sinteticas, claves_pronostico_sinteticas
        )


@pytest.mark.parametrize("periodo_invalido", ["2026-W00", "2025-W53", "2026-38"])
@pytest.mark.parametrize("en_claves_objetivo", [False, True])
def test_linea_base_ingenua_rechaza_periodos_iso_invalidos_sinteticos(
    periodo_invalido, en_claves_objetivo
):
    observaciones_reales_sinteticas = _observaciones_reales_sinteticas(
        [("P-001", periodo_invalido, 10.0)]
        if not en_claves_objetivo
        else [("P-001", "2026-W37", 10.0)]
    )
    claves_pronostico_sinteticas = _claves_pronostico_sinteticas(
        [("P-001", periodo_invalido)]
        if en_claves_objetivo
        else [("P-001", "2026-W38")]
    )

    with pytest.raises(ValueError, match="periodo"):
        linea_base_ingenua(
            observaciones_reales_sinteticas, claves_pronostico_sinteticas
        )


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


def test_comparar_metodos_disponibles_alinea_claves_y_reporta_exclusiones_sinteticas():
    observaciones_reales_sinteticas = pd.DataFrame(
        [
            ("P-001", "2026-W38", 10.0),
            ("P-002", "2026-W38", 20.0),
            ("P-001", "2026-W39", 30.0),
            ("P-002", "2026-W39", 40.0),
            ("P-003", "2026-W38", 50.0),
        ],
        columns=["parcela_id", "periodo", "y_real"],
    )
    predicciones_modelo_sinteticas = pd.DataFrame(
        [
            ("P-001", "2026-W39", 33.0),
            ("P-002", "2026-W38", 18.0),
            ("P-001", "2026-W38", 11.0),
        ],
        columns=["parcela_id", "periodo", "y_pred_modelo"],
    )
    predicciones_deterministas_sinteticas = pd.DataFrame(
        [
            ("P-003", "2026-W38", None),
            ("P-002", "2026-W39", 38.0),
            ("P-001", "2026-W39", 27.0),
            ("P-001", "2026-W38", 8.0),
            ("P-002", "2026-W38", 20.0),
        ],
        columns=["parcela_id", "periodo", "y_pred_base"],
    )
    predicciones_ingenuas_sinteticas = pd.DataFrame(
        [
            ("P-002", "2026-W39", None),
            ("P-001", "2026-W39", 29.0),
            ("P-003", "2026-W38", 45.0),
            ("P-002", "2026-W38", 25.0),
            ("P-001", "2026-W38", None),
        ],
        columns=["parcela_id", "periodo", "y_pred_ingenua"],
    )

    resultado = comparar_metodos_disponibles(
        observaciones_reales_sinteticas,
        predicciones_modelo_sinteticas,
        predicciones_deterministas_sinteticas,
        predicciones_ingenuas_sinteticas,
    )

    assert resultado.n_observaciones_candidatas == 5
    assert resultado.n_observaciones_incluidas == 2
    assert resultado.n_observaciones_excluidas == 3
    assert [
        (
            excluida.parcela_id,
            excluida.periodo,
            excluida.metodos_sin_prediccion,
        )
        for excluida in resultado.observaciones_excluidas
    ] == [
        ("P-001", "2026-W38", ("ingenua",)),
        ("P-002", "2026-W39", ("modelo", "ingenua")),
        ("P-003", "2026-W38", ("modelo", "determinista")),
    ]
    assert resultado.comparacion is not None
    assert resultado.comparacion.periodos == ("2026-W38", "2026-W39")
    assert resultado.comparacion.n_observaciones == 2
    assert resultado.comparacion.mae_predictivo == pytest.approx(2.5)
    assert resultado.comparacion.mae_determinista == pytest.approx(1.5)
    assert resultado.comparacion.mae_ingenua == pytest.approx(3.0)


def test_comparar_metodos_disponibles_reporta_sin_interseccion_sintetica():
    observaciones_reales_sinteticas = pd.DataFrame(
        [("P-001", "2026-W38", 10.0)],
        columns=["parcela_id", "periodo", "y_real"],
    )
    predicciones_modelo_sinteticas = pd.DataFrame(
        [("P-001", "2026-W38", 11.0)],
        columns=["parcela_id", "periodo", "y_pred_modelo"],
    )
    predicciones_deterministas_sinteticas = pd.DataFrame(
        [("P-001", "2026-W38", 9.0)],
        columns=["parcela_id", "periodo", "y_pred_base"],
    )
    predicciones_ingenuas_sinteticas = pd.DataFrame(
        [("P-001", "2026-W38", None)],
        columns=["parcela_id", "periodo", "y_pred_ingenua"],
    )

    resultado = comparar_metodos_disponibles(
        observaciones_reales_sinteticas,
        predicciones_modelo_sinteticas,
        predicciones_deterministas_sinteticas,
        predicciones_ingenuas_sinteticas,
    )

    assert resultado.comparacion is None
    assert resultado.n_observaciones_candidatas == 1
    assert resultado.n_observaciones_incluidas == 0
    assert resultado.n_observaciones_excluidas == 1
    assert resultado.observaciones_excluidas[0].metodos_sin_prediccion == (
        "ingenua",
    )


@pytest.mark.parametrize(
    "tabla_duplicada",
    [
        "reales",
        "modelo",
        "determinista",
        "ingenua",
    ],
)
def test_comparar_metodos_disponibles_rechaza_claves_duplicadas_sinteticas(
    tabla_duplicada,
):
    reales = pd.DataFrame(
        [
            ("P-001", "2026-W38", 10.0),
            ("P-001", "2026-W38", 12.0),
        ],
        columns=["parcela_id", "periodo", "y_real"],
    )
    modelo = pd.DataFrame(
        [("P-001", "2026-W38", 11.0)],
        columns=["parcela_id", "periodo", "y_pred_modelo"],
    )
    determinista = pd.DataFrame(
        [("P-001", "2026-W38", 9.0)],
        columns=["parcela_id", "periodo", "y_pred_base"],
    )
    ingenua = pd.DataFrame(
        [("P-001", "2026-W38", 8.0)],
        columns=["parcela_id", "periodo", "y_pred_ingenua"],
    )
    if tabla_duplicada == "modelo":
        modelo = pd.concat([modelo, modelo], ignore_index=True)
    elif tabla_duplicada == "determinista":
        determinista = pd.concat([determinista, determinista], ignore_index=True)
    elif tabla_duplicada == "ingenua":
        ingenua = pd.concat([ingenua, ingenua], ignore_index=True)

    with pytest.raises(ValueError, match="debe ser única"):
        comparar_metodos_disponibles(reales, modelo, determinista, ingenua)


@pytest.mark.parametrize(
    ("columna", "valor_invalido"),
    [
        ("y_pred_modelo", float("inf")),
        ("y_pred_base", float("-inf")),
        ("y_pred_ingenua", "desconocido"),
    ],
)
def test_comparar_metodos_disponibles_rechaza_predicciones_invalidas_sinteticas(
    columna, valor_invalido
):
    observaciones_reales_sinteticas = pd.DataFrame(
        [("P-001", "2026-W38", 10.0)],
        columns=["parcela_id", "periodo", "y_real"],
    )
    predicciones = {
        "y_pred_modelo": pd.DataFrame(
            [("P-001", "2026-W38", 11.0)],
            columns=["parcela_id", "periodo", "y_pred_modelo"],
        ),
        "y_pred_base": pd.DataFrame(
            [("P-001", "2026-W38", 9.0)],
            columns=["parcela_id", "periodo", "y_pred_base"],
        ),
        "y_pred_ingenua": pd.DataFrame(
            [("P-001", "2026-W38", 8.0)],
            columns=["parcela_id", "periodo", "y_pred_ingenua"],
        ),
    }
    predicciones[columna][columna] = predicciones[columna][columna].astype(object)
    predicciones[columna].loc[0, columna] = valor_invalido

    with pytest.raises(ValueError, match="números finitos o None"):
        comparar_metodos_disponibles(
            observaciones_reales_sinteticas,
            predicciones["y_pred_modelo"],
            predicciones["y_pred_base"],
            predicciones["y_pred_ingenua"],
        )


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
