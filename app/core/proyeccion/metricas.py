"""Métricas de evaluación de la proyección.

Incluye obligatoriamente la comparación contra una línea base ingenua
(seasonal naive / media histórica), sin la cual no se puede afirmar que el
modelo predictivo sirvió. Hyndman y Athanasopoulos (2021).

Responsable: Camilo — frente backend (T-14, T-20)
"""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from math import isfinite
from numbers import Real
import re

import pandas as pd


@dataclass(frozen=True)
class ResultadoComparacion:
    periodos: tuple[str, ...]
    n_observaciones: int
    mae_predictivo: float
    mae_determinista: float
    mae_ingenua: float


@dataclass(frozen=True)
class ObservacionExcluida:
    parcela_id: str
    periodo: str
    metodos_sin_prediccion: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoComparacionMetodos:
    comparacion: ResultadoComparacion | None
    n_observaciones_candidatas: int
    n_observaciones_incluidas: int
    n_observaciones_excluidas: int
    observaciones_excluidas: tuple[ObservacionExcluida, ...]


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


def _validar_claves_parcela_periodo(
    claves: pd.DataFrame, nombre: str
) -> list[tuple[str, date]]:
    if not isinstance(claves, pd.DataFrame):
        raise TypeError(f"{nombre} debe ser un pandas.DataFrame")
    if not claves.columns.is_unique:
        raise ValueError(f"Los nombres de columnas de {nombre} deben ser únicos")

    columnas_requeridas = ("parcela_id", "periodo")
    faltantes = [columna for columna in columnas_requeridas if columna not in claves]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en {nombre}: {', '.join(faltantes)}")
    if claves[["parcela_id", "periodo"]].isna().any().any():
        raise ValueError(f"parcela_id y periodo no pueden ser nulos en {nombre}")

    fechas = []
    for parcela_id, periodo in claves[["parcela_id", "periodo"]].itertuples(
        index=False, name=None
    ):
        if not isinstance(parcela_id, str) or not parcela_id.strip():
            raise ValueError(f"parcela_id debe ser texto no vacío en {nombre}")
        fechas.append(_fecha_inicio_semana_iso(periodo))

    if claves.duplicated(["parcela_id", "periodo"]).any():
        raise ValueError(
            f"Cada combinación de parcela_id y periodo debe ser única en {nombre}"
        )
    return list(zip(claves["parcela_id"].tolist(), fechas))


def linea_base_ingenua(
    observaciones_reales: pd.DataFrame,
    claves_pronostico: pd.DataFrame,
) -> pd.DataFrame:
    """Predice con la cosecha real de la semana ISO anterior de cada parcela.

    `observaciones_reales` requiere `parcela_id`, `periodo` y `y_real`.
    `claves_pronostico` requiere `parcela_id` y `periodo`. Devuelve las claves
    objetivo y `y_pred_ingenua`; el valor es ``None`` cuando no existe una
    observación para la semana anterior, y puede ser ``0.0`` si ese fue el
    valor real observado.
    """
    if not isinstance(observaciones_reales, pd.DataFrame):
        raise TypeError("observaciones_reales debe ser un pandas.DataFrame")
    if not observaciones_reales.columns.is_unique:
        raise ValueError(
            "Los nombres de columnas de observaciones_reales deben ser únicos"
        )
    if "y_real" not in observaciones_reales.columns:
        raise ValueError("Falta la columna requerida en observaciones_reales: y_real")

    columnas_clave = ["parcela_id", "periodo"]
    claves_reales = _validar_claves_parcela_periodo(
        observaciones_reales, "observaciones_reales"
    )
    claves_objetivo = _validar_claves_parcela_periodo(
        claves_pronostico, "claves_pronostico"
    )
    if claves_pronostico.empty:
        raise ValueError("claves_pronostico no puede estar vacío")

    valores_reales = []
    for valor in observaciones_reales["y_real"].tolist():
        if (
            isinstance(valor, bool)
            or not isinstance(valor, Real)
        ):
            raise ValueError("y_real debe contener solo números finitos")
        try:
            valor_float = float(valor)
        except (OverflowError, TypeError, ValueError) as exc:
            raise ValueError("y_real debe contener solo números finitos") from exc
        if not isfinite(valor_float):
            raise ValueError("y_real debe contener solo números finitos")
        valores_reales.append(valor_float)

    cosechas_por_clave = dict(zip(claves_reales, valores_reales))

    predicciones = [
        cosechas_por_clave.get((parcela_id, fecha - timedelta(days=7)))
        for parcela_id, fecha in claves_objetivo
    ]
    resultado = claves_pronostico[columnas_clave].copy()
    resultado["y_pred_ingenua"] = pd.array(predicciones, dtype=object)
    return resultado


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


def comparar_metodos_disponibles(
    observaciones_reales: pd.DataFrame,
    predicciones_modelo: pd.DataFrame,
    predicciones_deterministas: pd.DataFrame,
    predicciones_ingenuas: pd.DataFrame,
) -> ResultadoComparacionMetodos:
    """Compara los tres métodos solo donde existen todas sus predicciones.

    Cada tabla de predicciones requiere `parcela_id`, `periodo` y una columna
    de predicción: `y_pred_modelo`, `y_pred_base` o `y_pred_ingenua`.
    Una clave ausente o un valor nulo (`None`, `NaN` o `pd.NA`) indica
    indisponibilidad. Los MAE se calculan con `comparar()` sobre la
    intersección común. No genera predicciones ni presupone cómo se obtuvieron
    las observaciones reales.
    """
    if not isinstance(observaciones_reales, pd.DataFrame):
        raise TypeError("observaciones_reales debe ser un pandas.DataFrame")
    if not observaciones_reales.columns.is_unique:
        raise ValueError("Los nombres de columnas de observaciones_reales deben ser únicos")

    columnas_reales = ("parcela_id", "periodo", "y_real")
    faltantes_reales = [
        columna for columna in columnas_reales if columna not in observaciones_reales
    ]
    if faltantes_reales:
        raise ValueError(
            f"Faltan columnas requeridas en observaciones_reales: "
            f"{', '.join(faltantes_reales)}"
        )
    if observaciones_reales.empty:
        raise ValueError("observaciones_reales no puede estar vacío")
    _validar_claves_parcela_periodo(observaciones_reales, "observaciones_reales")

    reales = observaciones_reales.loc[:, list(columnas_reales)].copy()
    for valor in reales["y_real"].tolist():
        if (
            isinstance(valor, bool)
            or not isinstance(valor, Real)
            or not isfinite(float(valor))
        ):
            raise ValueError("y_real debe contener solo números finitos")

    definiciones_predicciones = (
        ("modelo", predicciones_modelo, "y_pred_modelo"),
        ("determinista", predicciones_deterministas, "y_pred_base"),
        ("ingenua", predicciones_ingenuas, "y_pred_ingenua"),
    )
    combinadas = reales
    columnas_metodo = []
    for nombre_metodo, predicciones, columna_prediccion in definiciones_predicciones:
        if not isinstance(predicciones, pd.DataFrame):
            raise TypeError(
                f"predicciones_{nombre_metodo}s debe ser un pandas.DataFrame"
            )
        if not predicciones.columns.is_unique:
            raise ValueError(
                f"Los nombres de columnas de predicciones_{nombre_metodo}s "
                "deben ser únicos"
            )
        columnas_requeridas = ("parcela_id", "periodo", columna_prediccion)
        faltantes = [
            columna for columna in columnas_requeridas if columna not in predicciones
        ]
        if faltantes:
            raise ValueError(
                f"Faltan columnas requeridas en predicciones_{nombre_metodo}s: "
                f"{', '.join(faltantes)}"
            )
        _validar_claves_parcela_periodo(predicciones, f"predicciones_{nombre_metodo}s")

        columna_interna = f"_prediccion_{nombre_metodo}"
        datos_prediccion = predicciones.loc[
            :, ["parcela_id", "periodo", columna_prediccion]
        ].rename(columns={columna_prediccion: columna_interna})
        for valor in datos_prediccion[columna_interna].tolist():
            if pd.isna(valor):
                continue
            if (
                isinstance(valor, bool)
                or not isinstance(valor, Real)
                or not isfinite(float(valor))
            ):
                raise ValueError(
                    f"{columna_prediccion} debe contener números finitos o None"
                )
        combinadas = combinadas.merge(
            datos_prediccion,
            on=["parcela_id", "periodo"],
            how="left",
            validate="one_to_one",
            sort=False,
        )
        columnas_metodo.append((nombre_metodo, columna_interna))

    excluidas = []
    incluidas = []
    for _, fila in combinadas.iterrows():
        faltantes = tuple(
            nombre
            for nombre, columna in columnas_metodo
            if pd.isna(fila[columna])
        )
        if faltantes:
            excluidas.append(
                ObservacionExcluida(
                    parcela_id=fila["parcela_id"],
                    periodo=fila["periodo"],
                    metodos_sin_prediccion=faltantes,
                )
            )
        else:
            incluidas.append(fila)

    if incluidas:
        datos_comparacion = pd.DataFrame(
            [
                {
                    "parcela_id": fila["parcela_id"],
                    "periodo": fila["periodo"],
                    "y_real": fila["y_real"],
                    "y_pred_modelo": fila["_prediccion_modelo"],
                    "y_pred_base": fila["_prediccion_determinista"],
                    "y_pred_ingenua": fila["_prediccion_ingenua"],
                }
                for fila in incluidas
            ],
            columns=[
                "parcela_id",
                "periodo",
                "y_real",
                "y_pred_modelo",
                "y_pred_base",
                "y_pred_ingenua",
            ],
        )
        comparacion = comparar(datos_comparacion)
    else:
        comparacion = None

    return ResultadoComparacionMetodos(
        comparacion=comparacion,
        n_observaciones_candidatas=len(reales),
        n_observaciones_incluidas=len(incluidas),
        n_observaciones_excluidas=len(excluidas),
        observaciones_excluidas=tuple(excluidas),
    )
