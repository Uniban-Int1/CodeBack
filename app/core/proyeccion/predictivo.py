"""Modelo predictivo de proyección de cosecha (scikit-learn).

Esta interfaz permite experimentación técnica. La evaluación temporal y la
validación agronómica con datos reales son etapas separadas pendientes.

REGLA (D-003): este modelo solo se adopta si supera de forma medible al modelo base
Y a una línea base ingenua. Si no lo supera, se conserva el determinista y se
documenta la razón en DECISIONES.md. Eso no es un fracaso: es el resultado.

Responsable: Camilo — frente backend (T-14)
"""
from datetime import date
import re
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit

from app.core.proyeccion.metricas import mae

METODO = "predictivo-v1"


@dataclass(frozen=True)
class ModeloEntrenado:
    estimador: LinearRegression
    columnas_predictoras: tuple[str, ...]
    columna_objetivo: str


@dataclass(frozen=True)
class FoldTemporal:
    indices_entrenamiento: tuple[int, ...]
    indices_validacion: tuple[int, ...]
    periodos_entrenamiento: tuple[str, ...]
    periodos_validacion: tuple[str, ...]


@dataclass(frozen=True)
class ParticionesTemporales:
    folds: tuple[FoldTemporal, ...]
    indices_holdout: tuple[int, ...]
    periodos_holdout: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoFoldEvaluacion:
    numero_fold: int
    periodos_entrenamiento: tuple[str, ...]
    periodos_evaluacion: tuple[str, ...]
    n_observaciones: int
    mae: float


@dataclass(frozen=True)
class ResultadoHoldoutEvaluacion:
    periodos_entrenamiento: tuple[str, ...]
    periodos_evaluacion: tuple[str, ...]
    n_observaciones: int
    mae: float


@dataclass(frozen=True)
class ResultadoEvaluacionTemporal:
    folds: tuple[ResultadoFoldEvaluacion, ...]
    holdout: ResultadoHoldoutEvaluacion


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


def _validar_claves_unicas(
    data: pd.DataFrame, columna_periodo: str = "periodo"
) -> None:
    columnas_clave = ("parcela_id", columna_periodo)
    if all(columna in data.columns for columna in columnas_clave):
        if data.duplicated(list(columnas_clave)).any():
            raise ValueError(
                f"Cada combinación de parcela_id y {columna_periodo} debe ser única"
            )


def _fecha_inicio_semana_iso(periodo: object) -> date:
    if (
        not isinstance(periodo, str)
        or re.fullmatch(r"[0-9]{4}-W[0-9]{2}", periodo) is None
    ):
        raise ValueError("periodo debe tener formato ISO week YYYY-Www")
    try:
        anio, semana = int(periodo[:4]), int(periodo[6:])
        return date.fromisocalendar(anio, semana, 1)
    except ValueError as exc:
        raise ValueError(f"periodo ISO week inválido: {periodo}") from exc


def particiones_temporales(
    observaciones: pd.DataFrame,
    *,
    columna_periodo: str,
    num_folds: int,
    num_periodos_holdout: int,
) -> ParticionesTemporales:
    """Genera folds expansivos y holdout final agrupados por periodo ISO semanal.

    Los índices devueltos son posiciones de fila para usar con ``DataFrame.iloc``,
    por lo que mantienen la correspondencia aunque el índice original se repita.
    Los folds se crean solo con periodos anteriores al holdout.
    """
    _validar_dataframe(observaciones)
    if not isinstance(columna_periodo, str) or not columna_periodo.strip():
        raise ValueError("columna_periodo debe ser un nombre no vacío")
    if columna_periodo not in observaciones.columns:
        raise ValueError(f"Falta la columna de periodo requerida: {columna_periodo}")
    if (
        isinstance(num_folds, bool)
        or not isinstance(num_folds, int)
        or num_folds < 1
    ):
        raise ValueError("num_folds debe ser un entero positivo")
    if (
        isinstance(num_periodos_holdout, bool)
        or not isinstance(num_periodos_holdout, int)
        or num_periodos_holdout < 1
    ):
        raise ValueError("num_periodos_holdout debe ser un entero positivo")

    _validar_claves_unicas(observaciones, columna_periodo)

    fechas_por_periodo: dict[str, date] = {}
    posiciones_por_periodo: dict[str, list[int]] = {}
    for posicion, periodo in enumerate(observaciones[columna_periodo].tolist()):
        fecha = _fecha_inicio_semana_iso(periodo)
        if periodo in fechas_por_periodo and fechas_por_periodo[periodo] != fecha:
            raise ValueError(f"periodo ISO week inválido: {periodo}")
        fechas_por_periodo[periodo] = fecha
        posiciones_por_periodo.setdefault(periodo, []).append(posicion)

    periodos_ordenados = tuple(
        sorted(fechas_por_periodo, key=fechas_por_periodo.__getitem__)
    )
    if num_periodos_holdout >= len(periodos_ordenados):
        raise ValueError(
            "debe quedar al menos un periodo antes del holdout"
        )

    periodos_pre_holdout = periodos_ordenados[:-num_periodos_holdout]
    if len(periodos_pre_holdout) <= num_folds:
        raise ValueError(
            "periodos insuficientes para el número de folds solicitado"
        )

    folds: list[FoldTemporal] = []
    validador = TimeSeriesSplit(n_splits=num_folds)
    for posiciones_train, posiciones_validacion in validador.split(
        np.arange(len(periodos_pre_holdout))
    ):
        periodos_train = tuple(
            periodos_pre_holdout[posicion] for posicion in posiciones_train
        )
        periodos_validacion = tuple(
            periodos_pre_holdout[posicion] for posicion in posiciones_validacion
        )
        indices_train = tuple(
            posicion
            for periodo in periodos_train
            for posicion in posiciones_por_periodo[periodo]
        )
        indices_validacion = tuple(
            posicion
            for periodo in periodos_validacion
            for posicion in posiciones_por_periodo[periodo]
        )
        folds.append(
            FoldTemporal(
                indices_entrenamiento=indices_train,
                indices_validacion=indices_validacion,
                periodos_entrenamiento=periodos_train,
                periodos_validacion=periodos_validacion,
            )
        )

    periodos_holdout = periodos_ordenados[-num_periodos_holdout:]
    indices_holdout = tuple(
        posicion
        for periodo in periodos_holdout
        for posicion in posiciones_por_periodo[periodo]
    )
    return ParticionesTemporales(
        folds=tuple(folds),
        indices_holdout=indices_holdout,
        periodos_holdout=periodos_holdout,
    )


def evaluar_temporal(
    observaciones: pd.DataFrame,
    *,
    columna_periodo: str,
    columnas_predictoras: Sequence[str],
    columna_objetivo: str,
    num_folds: int,
    num_periodos_holdout: int,
) -> ResultadoEvaluacionTemporal:
    """Entrena y evalúa folds expansivos y un holdout final por separado.

    Devuelve métricas técnicas para cada partición. No compara con otros
    métodos ni constituye validación agronómica de datos sintéticos.
    """
    if not isinstance(observaciones, pd.DataFrame):
        raise TypeError("observaciones debe ser un pandas.DataFrame")
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

    columnas_requeridas = (*columnas_predictoras, columna_objetivo)
    faltantes = [columna for columna in columnas_requeridas if columna not in observaciones]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(faltantes)}")

    particiones = particiones_temporales(
        observaciones,
        columna_periodo=columna_periodo,
        num_folds=num_folds,
        num_periodos_holdout=num_periodos_holdout,
    )

    resultados_folds: list[ResultadoFoldEvaluacion] = []
    for numero_fold, fold in enumerate(particiones.folds, start=1):
        datos_entrenamiento = observaciones.iloc[
            list(fold.indices_entrenamiento)
        ]
        datos_evaluacion = observaciones.iloc[list(fold.indices_validacion)]
        modelo = entrenar(
            datos_entrenamiento,
            columnas_predictoras=columnas_predictoras,
            columna_objetivo=columna_objetivo,
        )
        predicciones = predecir(
            modelo,
            datos_evaluacion.loc[:, list(columnas_predictoras)],
        )
        resultados_folds.append(
            ResultadoFoldEvaluacion(
                numero_fold=numero_fold,
                periodos_entrenamiento=fold.periodos_entrenamiento,
                periodos_evaluacion=fold.periodos_validacion,
                n_observaciones=len(datos_evaluacion),
                mae=mae(
                    datos_evaluacion[columna_objetivo].tolist(),
                    predicciones.tolist(),
                ),
            )
        )

    indices_holdout = set(particiones.indices_holdout)
    indices_entrenamiento_holdout = tuple(
        posicion
        for posicion in range(len(observaciones))
        if posicion not in indices_holdout
    )
    datos_entrenamiento_holdout = observaciones.iloc[
        list(indices_entrenamiento_holdout)
    ]
    datos_holdout = observaciones.iloc[list(particiones.indices_holdout)]
    modelo_holdout = entrenar(
        datos_entrenamiento_holdout,
        columnas_predictoras=columnas_predictoras,
        columna_objetivo=columna_objetivo,
    )
    predicciones_holdout = predecir(
        modelo_holdout,
        datos_holdout.loc[:, list(columnas_predictoras)],
    )
    periodos_entrenamiento_holdout = tuple(
        sorted(
            set(observaciones[columna_periodo]) - set(particiones.periodos_holdout),
            key=_fecha_inicio_semana_iso,
        )
    )
    resultado_holdout = ResultadoHoldoutEvaluacion(
        periodos_entrenamiento=periodos_entrenamiento_holdout,
        periodos_evaluacion=particiones.periodos_holdout,
        n_observaciones=len(datos_holdout),
        mae=mae(
            datos_holdout[columna_objetivo].tolist(),
            predicciones_holdout.tolist(),
        ),
    )
    return ResultadoEvaluacionTemporal(
        folds=tuple(resultados_folds),
        holdout=resultado_holdout,
    )


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
