"""Métricas de evaluación de la proyección.

Incluye obligatoriamente la comparación contra una línea base ingenua
(seasonal naive / media histórica), sin la cual no se puede afirmar que el
modelo predictivo sirvió. Hyndman y Athanasopoulos (2021).

Responsable: Camilo — frente backend (T-14, T-20)
"""
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from numbers import Real

import pandas as pd


@dataclass(frozen=True)
class ResultadoComparacion:
    periodos: tuple[str, ...]
    n_observaciones: int
    mae_predictivo: float
    mae_determinista: float
    mae_ingenua: float


def linea_base_ingenua(serie):
    """Seasonal naive: el valor de la semana anterior."""
    raise NotImplementedError("T-14")


def mae(y_real: Iterable[Real], y_pred: Iterable[Real]) -> float:
    """Calcula MAE para dos colecciones no vacías de valores numéricos finitos."""
    try:
        reales = list(y_real)
        predichos = list(y_pred)
    except TypeError as exc:
        raise TypeError("y_real e y_pred deben ser iterables numéricos") from exc

    if not reales or not predichos:
        raise ValueError("y_real e y_pred no pueden estar vacíos")
    if len(reales) != len(predichos):
        raise ValueError("y_real e y_pred deben tener la misma longitud")

    errores = []
    for real, predicho in zip(reales, predichos):
        if (
            isinstance(real, bool)
            or isinstance(predicho, bool)
            or not isinstance(real, Real)
            or not isinstance(predicho, Real)
            or not isfinite(float(real))
            or not isfinite(float(predicho))
        ):
            raise ValueError("y_real e y_pred deben contener solo números finitos")
        errores.append(abs(float(real) - float(predicho)))

    return sum(errores) / len(errores)


def comparar(observaciones: pd.DataFrame) -> ResultadoComparacion:
    """Compara MAE usando las mismas filas identificadas por parcela y periodo.

    `observaciones` debe contener `parcela_id`, `periodo`, `y_real`,
    `y_pred_modelo`, `y_pred_base` y `y_pred_ingenua`. Cada fila aporta una
    misma observación a los tres métodos.
    """
    if not isinstance(observaciones, pd.DataFrame):
        raise TypeError("observaciones debe ser un pandas.DataFrame")

    columnas_requeridas = (
        "parcela_id",
        "periodo",
        "y_real",
        "y_pred_modelo",
        "y_pred_base",
        "y_pred_ingenua",
    )
    faltantes = [columna for columna in columnas_requeridas if columna not in observaciones]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(faltantes)}")
    if observaciones.empty:
        raise ValueError("observaciones no puede estar vacío")

    claves = observaciones[["parcela_id", "periodo"]]
    if claves.isna().any().any():
        raise ValueError("parcela_id y periodo no pueden ser nulos")
    if not claves.map(lambda valor: isinstance(valor, str) and bool(valor.strip())).all().all():
        raise ValueError("parcela_id y periodo deben ser textos no vacíos")
    if claves.duplicated().any():
        raise ValueError("Cada combinación de parcela_id y periodo debe ser única")

    y_real = observaciones["y_real"].tolist()
    periodos = tuple(dict.fromkeys(observaciones["periodo"].tolist()))
    return ResultadoComparacion(
        periodos=periodos,
        n_observaciones=len(observaciones),
        mae_predictivo=mae(y_real, observaciones["y_pred_modelo"].tolist()),
        mae_determinista=mae(y_real, observaciones["y_pred_base"].tolist()),
        mae_ingenua=mae(y_real, observaciones["y_pred_ingenua"].tolist()),
    )
