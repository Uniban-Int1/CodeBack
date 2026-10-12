"""Modelo predictivo de proyección de cosecha (scikit-learn).

Esta interfaz permite experimentación técnica. La evaluación temporal y la
validación agronómica con datos reales son etapas separadas pendientes.

REGLA (D-003): este modelo solo se adopta si supera de forma medible al modelo base
Y a una línea base ingenua. Si no lo supera, se conserva el determinista y se
documenta la razón en DECISIONES.md. Eso no es un fracaso: es el resultado.

Responsable: Camilo — frente backend (T-14)
"""
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from sklearn.linear_model import LinearRegression

METODO = "predictivo-v1"


@dataclass(frozen=True)
class ModeloEntrenado:
    estimador: LinearRegression
    columnas_predictoras: tuple[str, ...]
    columna_objetivo: str


def _validar_dataframe(data: pd.DataFrame) -> None:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("los datos deben ser un pandas.DataFrame")
    if data.empty:
        raise ValueError("los datos no pueden estar vacíos")
    if not data.columns.is_unique:
        raise ValueError("los nombres de columnas deben ser únicos")


def _validar_valores_numericos(data: pd.DataFrame, columnas: Sequence[str]) -> None:
    for columna in columnas:
        valores = data[columna]
        if valores.isna().any():
            raise ValueError(f"{columna} no puede contener valores nulos")
        if not is_numeric_dtype(valores.dtype) or is_bool_dtype(valores.dtype):
            raise ValueError(f"{columna} debe contener valores numéricos")
        arreglo = valores.to_numpy()
        if np.iscomplexobj(arreglo):
            raise ValueError(f"{columna} debe contener valores numéricos finitos")
        try:
            valores_float = valores.to_numpy(dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                f"{columna} debe contener valores numéricos finitos"
            ) from exc
        if not np.isfinite(valores_float).all():
            raise ValueError(f"{columna} debe contener valores numéricos finitos")


def _validar_claves_unicas(data: pd.DataFrame) -> None:
    claves = ("parcela_id", "periodo")
    if all(columna in data.columns for columna in claves):
        if data.duplicated(list(claves)).any():
            raise ValueError("Cada combinación de parcela_id y periodo debe ser única")


def entrenar(
    observaciones: pd.DataFrame,
    *,
    columnas_predictoras: Sequence[str],
    columna_objetivo: str,
) -> ModeloEntrenado:
    """Entrena regresión lineal con las columnas explícitamente seleccionadas.

    Las observaciones deben incluir características y una variable objetivo
    numéricas. No realiza imputación, codificación ni partición temporal.
    """
    _validar_dataframe(observaciones)

    if isinstance(columnas_predictoras, str) or not isinstance(
        columnas_predictoras, Sequence
    ):
        raise TypeError("columnas_predictoras debe ser una secuencia de nombres")
    if not columnas_predictoras or any(
        not isinstance(columna, str) or not columna.strip()
        for columna in columnas_predictoras
    ):
        raise ValueError("columnas_predictoras debe contener nombres no vacíos")
    if len(set(columnas_predictoras)) != len(columnas_predictoras):
        raise ValueError("columnas_predictoras no puede contener nombres duplicados")
    if not isinstance(columna_objetivo, str) or not columna_objetivo.strip():
        raise ValueError("columna_objetivo debe ser un nombre no vacío")
    if columna_objetivo in columnas_predictoras:
        raise ValueError("la columna objetivo no puede ser una característica")

    _validar_claves_unicas(observaciones)

    columnas_modelo = (*columnas_predictoras, columna_objetivo)
    faltantes = [columna for columna in columnas_modelo if columna not in observaciones]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(faltantes)}")
    _validar_valores_numericos(observaciones, columnas_modelo)

    estimador = LinearRegression()
    estimador.fit(
        observaciones.loc[:, list(columnas_predictoras)].to_numpy(),
        observaciones[columna_objetivo].to_numpy(),
    )
    return ModeloEntrenado(
        estimador=estimador,
        columnas_predictoras=tuple(columnas_predictoras),
        columna_objetivo=columna_objetivo,
    )


def predecir(modelo: ModeloEntrenado, X: pd.DataFrame) -> np.ndarray:
    """Predice para filas que incluyan todas las características entrenadas."""
    if not isinstance(modelo, ModeloEntrenado):
        raise TypeError("modelo debe ser un ModeloEntrenado")
    _validar_dataframe(X)

    faltantes = [
        columna for columna in modelo.columnas_predictoras if columna not in X.columns
    ]
    if faltantes:
        raise ValueError(f"Faltan características requeridas: {', '.join(faltantes)}")
    _validar_claves_unicas(X)
    _validar_valores_numericos(X, modelo.columnas_predictoras)

    return modelo.estimador.predict(
        X.loc[:, list(modelo.columnas_predictoras)].to_numpy()
    )
