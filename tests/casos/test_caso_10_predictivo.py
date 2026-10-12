"""Pruebas técnicas del modelo predictivo con datos sintéticos."""
import numpy as np
import pandas as pd
import pytest

from app.core.proyeccion.predictivo import (
    ModeloEntrenado,
    entrenar,
    particiones_temporales,
    predecir,
)


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


@pytest.fixture
def observaciones_temporales_sinteticas():
    periodos = (
        "2025-W51",
        "2025-W52",
        "2026-W01",
        "2026-W02",
        "2026-W03",
        "2026-W04",
        "2026-W05",
        "2026-W06",
    )
    filas = [
        {
            "parcela_id": f"P-{parcela:03d}",
            "periodo": periodo,
            "caracteristica_sintetica": float(parcela),
            "objetivo_sintetico": float(indice + parcela),
        }
        for indice, periodo in enumerate(reversed(periodos))
        for parcela in (1, 2)
    ]
    observaciones = pd.DataFrame(filas)
    observaciones.index = [indice // 2 for indice in range(len(observaciones))]
    return observaciones


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


def test_particiones_temporales_ordena_periodos_iso_y_separa_holdout_sintetico(
    observaciones_temporales_sinteticas,
):
    particiones = particiones_temporales(
        observaciones_temporales_sinteticas,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=2,
    )

    assert particiones.periodos_holdout == ("2026-W05", "2026-W06")
    assert len(particiones.folds) == 2
    assert not set(particiones.periodos_holdout).intersection(
        periodo
        for fold in particiones.folds
        for periodo in (*fold.periodos_entrenamiento, *fold.periodos_validacion)
    )


def test_particiones_temporales_no_filtra_futuro_y_mantiene_periodos_juntos(
    observaciones_temporales_sinteticas,
):
    datos = observaciones_temporales_sinteticas
    particiones = particiones_temporales(
        datos,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=2,
    )

    for fold in particiones.folds:
        periodos_train = set(fold.periodos_entrenamiento)
        periodos_validacion = set(fold.periodos_validacion)
        assert max(periodos_train) < min(periodos_validacion)
        assert periodos_train.isdisjoint(periodos_validacion)

        periodos_indices_train = set(
            datos.iloc[list(fold.indices_entrenamiento)]["periodo"]
        )
        periodos_indices_validacion = set(
            datos.iloc[list(fold.indices_validacion)]["periodo"]
        )
        assert periodos_indices_train == periodos_train
        assert periodos_indices_validacion == periodos_validacion
        assert set(fold.indices_entrenamiento) == {
            posicion
            for posicion, periodo in enumerate(datos["periodo"])
            if periodo in periodos_train
        }
        assert set(fold.indices_validacion) == {
            posicion
            for posicion, periodo in enumerate(datos["periodo"])
            if periodo in periodos_validacion
        }

    assert set(datos.iloc[list(particiones.indices_holdout)]["periodo"]) == set(
        particiones.periodos_holdout
    )


def test_particiones_temporales_usa_ventanas_expansivas_sinteticas(
    observaciones_temporales_sinteticas,
):
    particiones = particiones_temporales(
        observaciones_temporales_sinteticas,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=2,
    )
    tamaños_entrenamiento = [
        len(fold.periodos_entrenamiento) for fold in particiones.folds
    ]

    assert tamaños_entrenamiento == sorted(tamaños_entrenamiento)
    assert tamaños_entrenamiento[0] < tamaños_entrenamiento[1]
    assert particiones.folds[0].periodos_entrenamiento == (
        "2025-W51",
        "2025-W52",
    )
    assert particiones.folds[1].periodos_entrenamiento == (
        "2025-W51",
        "2025-W52",
        "2026-W01",
        "2026-W02",
    )


def test_particiones_temporales_permite_huecos_sin_inventar_semanas():
    observaciones_sinteticas_con_hueco = pd.DataFrame(
        {
            "periodo": [
                "2026-W01",
                "2026-W03",
                "2026-W05",
                "2026-W07",
                "2026-W09",
            ]
        }
    )

    particiones = particiones_temporales(
        observaciones_sinteticas_con_hueco,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=1,
    )

    assert particiones.periodos_holdout == ("2026-W09",)
    assert tuple(
        periodo
        for fold in particiones.folds
        for periodo in fold.periodos_validacion
    ) == ("2026-W05", "2026-W07")


@pytest.mark.parametrize(
    ("observaciones", "columna_periodo", "num_folds", "num_periodos_holdout"),
    [
        (pd.DataFrame({"periodo": []}), "periodo", 1, 1),
        (pd.DataFrame({"otra": ["2026-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": [None, "2026-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": [202601, "2026-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": ["2026-W00", "2026-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": ["2026-W54", "2027-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": ["2026-01", "2026-W01"]}), "periodo", 1, 1),
        (pd.DataFrame({"periodo": ["2026-W01", "2026-W02"]}), "periodo", 0, 1),
        (pd.DataFrame({"periodo": ["2026-W01", "2026-W02"]}), "periodo", 1, 0),
        (
            pd.DataFrame(
                {"periodo": ["2026-W01", "2026-W02", "2026-W03"]}
            ),
            "periodo",
            2,
            1,
        ),
        (
            pd.DataFrame(
                {"periodo": ["2026-W01", "2026-W02", "2026-W03"]}
            ),
            "periodo",
            1,
            3,
        ),
    ],
)
def test_particiones_temporales_rechaza_entradas_o_configuracion_invalida(
    observaciones, columna_periodo, num_folds, num_periodos_holdout
):
    with pytest.raises((TypeError, ValueError)):
        particiones_temporales(
            observaciones,
            columna_periodo=columna_periodo,
            num_folds=num_folds,
            num_periodos_holdout=num_periodos_holdout,
        )


def test_particiones_temporales_rechaza_claves_parcela_periodo_duplicadas():
    observaciones_sinteticas_duplicadas = pd.DataFrame(
        {
            "parcela_id": ["P-001", "P-001", "P-002", "P-001"],
            "periodo": [
                "2026-W01",
                "2026-W01",
                "2026-W02",
                "2026-W03",
            ],
        }
    )

    with pytest.raises(ValueError, match="debe ser única"):
        particiones_temporales(
            observaciones_sinteticas_duplicadas,
            columna_periodo="periodo",
            num_folds=1,
            num_periodos_holdout=1,
        )


def test_particiones_temporales_rechaza_claves_parcela_semana_duplicadas():
    observaciones_sinteticas_duplicadas = pd.DataFrame(
        {
            "parcela_id": ["P-001", "P-001", "P-002", "P-001"],
            "semana": [
                "2026-W01",
                "2026-W01",
                "2026-W02",
                "2026-W03",
            ],
        }
    )

    with pytest.raises(ValueError, match="parcela_id y semana"):
        particiones_temporales(
            observaciones_sinteticas_duplicadas,
            columna_periodo="semana",
            num_folds=1,
            num_periodos_holdout=1,
        )


def test_periodo_iso_acepta_semana_53_en_anio_valido_sintetico():
    observaciones_sinteticas = pd.DataFrame(
        {
            "periodo": [
                "2020-W52",
                "2020-W53",
                "2021-W01",
                "2021-W02",
                "2021-W03",
            ]
        }
    )

    particiones = particiones_temporales(
        observaciones_sinteticas,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=1,
    )

    assert particiones.folds[0].periodos_entrenamiento == (
        "2020-W52",
        "2020-W53",
    )
    assert particiones.folds[0].periodos_validacion == ("2021-W01",)
    assert particiones.folds[1].periodos_entrenamiento == (
        "2020-W52",
        "2020-W53",
        "2021-W01",
    )
    assert particiones.periodos_holdout == ("2021-W03",)


def test_periodo_iso_rechaza_semana_53_en_anio_invalido_sintetico():
    observaciones_sinteticas = pd.DataFrame(
        {"periodo": ["2021-W52", "2021-W53", "2022-W01"]}
    )

    with pytest.raises(ValueError, match="periodo ISO week inválido"):
        particiones_temporales(
            observaciones_sinteticas,
            columna_periodo="periodo",
            num_folds=2,
            num_periodos_holdout=1,
        )


def test_particiones_temporales_conserva_posiciones_con_indice_desordenado():
    observaciones_sinteticas = pd.DataFrame(
        {
            "parcela_id": [
                "P-003",
                "P-001",
                "P-002",
                "P-001",
                "P-003",
                "P-002",
                "P-004",
            ],
            "periodo": [
                "2026-W03",
                "2026-W01",
                "2026-W02",
                "2026-W03",
                "2026-W01",
                "2026-W01",
                "2026-W04",
            ],
            "identificador_fila_sintetica": [
                "fila-0",
                "fila-1",
                "fila-2",
                "fila-3",
                "fila-4",
                "fila-5",
                "fila-6",
            ],
        },
        index=[40, 5, 90, 2, 71, 13, 1],
    )

    particiones = particiones_temporales(
        observaciones_sinteticas,
        columna_periodo="periodo",
        num_folds=2,
        num_periodos_holdout=1,
    )

    filas_holdout = observaciones_sinteticas.iloc[list(particiones.indices_holdout)][
        "identificador_fila_sintetica"
    ].tolist()
    filas_entrenamiento = observaciones_sinteticas.iloc[
        list(particiones.folds[0].indices_entrenamiento)
    ]["identificador_fila_sintetica"].tolist()
    filas_validacion = observaciones_sinteticas.iloc[
        list(particiones.folds[0].indices_validacion)
    ]["identificador_fila_sintetica"].tolist()

    assert filas_holdout == ["fila-6"]
    assert filas_entrenamiento == ["fila-1", "fila-4", "fila-5"]
    assert filas_validacion == ["fila-2"]
    assert particiones.folds[1].indices_entrenamiento == (1, 4, 5, 2)
    assert particiones.folds[1].indices_validacion == (0, 3)
