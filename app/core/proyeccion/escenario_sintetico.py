"""Escenario SINTÉTICO para evaluar el modelo predictivo frente al determinista (T-14).

NO son datos de Unibán (D-006, D-019). La "cosecha real" la genera este módulo con
supuestos explícitos, así que el resultado refleja esos supuestos, no el campo:

- ciclo real de 11.5 semanas, mientras la fórmula determinista asume 10.5
  (config/parametros.yaml) — un sesgo conocido de la fórmula;
- estacionalidad de ±15 % con periodo de 13 semanas, que la fórmula no modela;
- ruido multiplicativo de 5 % y reaforamientos semanales con ±3 % de variación.

Lo que sí demuestra es que el pipeline de evaluación funciona de punta a punta:
particiones temporales expansivas sin fuga, holdout final, los tres métodos
comparados sobre las mismas claves y la regla de adopción D-003 aplicada.
"""
from functools import lru_cache
from math import cos, pi, sin

import numpy as np
import pandas as pd

from app.config import parametros
from app.core.proyeccion.base import Aforamiento, proyectar
from app.core.proyeccion.predictivo import evaluar_temporal_integrada, particiones_temporales

ADVERTENCIA = (
    "Datos sintéticos generados por app/core/proyeccion/escenario_sintetico.py. "
    "No son registros de Unibán y no constituyen validación productiva (D-006, D-019)."
)
SUPUESTOS = {
    "parcelas": 8,
    "semanas": 24,
    "ciclo_real_semanas": 11.5,
    "amplitud_estacional": 0.15,
    "periodo_estacional_semanas": 13,
    "ruido_relativo": 0.05,
    "num_folds": 6,
    "num_periodos_holdout": 1,
}
PREDICTORAS = ("num_plantas", "calidad_confianza", "estacional_sin", "estacional_cos")


def _periodos(primera_semana: int, cantidad: int) -> list[str]:
    return [f"2026-W{semana:02d}" for semana in range(primera_semana, primera_semana + cantidad)]


def generar_observaciones(semilla: int = 2026) -> pd.DataFrame:
    """Tabla sintética parcela-semana con características y cosecha "real" simulada."""
    rng = np.random.default_rng(semilla)
    s = SUPUESTOS
    filas = []
    plantas_base = rng.integers(1200, 2600, size=s["parcelas"])
    confianza_base = rng.uniform(0.75, 0.95, size=s["parcelas"])
    for numero, periodo in enumerate(_periodos(10, s["semanas"])):
        angulo = 2 * pi * numero / s["periodo_estacional_semanas"]
        for i in range(s["parcelas"]):
            plantas = int(plantas_base[i] * rng.uniform(0.97, 1.03))
            cosecha = (
                plantas
                / s["ciclo_real_semanas"]
                * (1 + s["amplitud_estacional"] * sin(angulo))
                * rng.normal(1.0, s["ruido_relativo"])
            )
            filas.append({
                "parcela_id": f"P-SINTETICA-{i + 1:02d}",
                "periodo": periodo,
                "num_plantas": float(plantas),
                "calidad_confianza": round(float(confianza_base[i]), 2),
                "estacional_sin": sin(angulo),
                "estacional_cos": cos(angulo),
                "cosecha_real": round(cosecha, 2),
            })
    return pd.DataFrame(filas)


def _predicciones_deterministas(bloque: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Aplica la fórmula determinista real (proyectar) a cada fila del bloque evaluado."""
    filas = []
    for fila in bloque.itertuples(index=False):
        proyeccion = proyectar(
            Aforamiento(fila.parcela_id, int(fila.num_plantas), 0.0, fila.calidad_confianza),
            periodo=fila.periodo,
            ciclo_racimo_semanas=params["proyeccion"]["ciclo_racimo_semanas"],
            factor_perdida=params["proyeccion"]["factor_perdida"],
        )
        filas.append({"parcela_id": fila.parcela_id, "periodo": fila.periodo, "y_pred_base": proyeccion.volumen_racimos})
    return pd.DataFrame(filas)


def _bloque(nombre: str, periodos_eval: tuple[str, ...], comparacion) -> dict:
    c = comparacion.comparacion
    return {
        "bloque": nombre,
        "periodos_evaluacion": list(periodos_eval),
        "n_comparadas": comparacion.n_observaciones_incluidas,
        "n_excluidas": comparacion.n_observaciones_excluidas,
        "mae_predictivo": None if c is None else round(c.mae_predictivo, 2),
        "mae_determinista": None if c is None else round(c.mae_determinista, 2),
        "mae_ingenua": None if c is None else round(c.mae_ingenua, 2),
    }


@lru_cache
def evaluar_escenario_sintetico(semilla: int = 2026) -> dict:
    """Corre la evaluación temporal de los tres métodos y aplica D-003 sobre el holdout."""
    params = parametros()
    observaciones = generar_observaciones(semilla)
    particiones = particiones_temporales(
        observaciones,
        columna_periodo="periodo",
        num_folds=SUPUESTOS["num_folds"],
        num_periodos_holdout=SUPUESTOS["num_periodos_holdout"],
    )
    deterministas = {
        f"fold_{n}": _predicciones_deterministas(observaciones.iloc[list(f.indices_validacion)], params)
        for n, f in enumerate(particiones.folds, start=1)
    }
    deterministas["holdout"] = _predicciones_deterministas(
        observaciones.iloc[list(particiones.indices_holdout)], params
    )
    resultado = evaluar_temporal_integrada(
        observaciones,
        columna_periodo="periodo",
        columnas_predictoras=PREDICTORAS,
        columna_objetivo="cosecha_real",
        predicciones_deterministas=deterministas,
        num_folds=SUPUESTOS["num_folds"],
        num_periodos_holdout=SUPUESTOS["num_periodos_holdout"],
    )
    bloques = [_bloque(f"fold_{f.numero_fold}", f.periodos_evaluacion, f.comparacion) for f in resultado.folds]
    holdout = _bloque("holdout", resultado.holdout.periodos_evaluacion, resultado.holdout.comparacion)

    supera = (
        holdout["mae_predictivo"] is not None
        and holdout["mae_predictivo"] < holdout["mae_determinista"]
        and holdout["mae_predictivo"] < holdout["mae_ingenua"]
    )
    texto = (
        "En este escenario sintético el predictivo supera a ambos métodos en el holdout. "
        if supera else
        "En este escenario sintético el predictivo NO supera a ambos métodos en el holdout. "
    ) + (
        "No se adopta en producción: D-003 exige compararlo con cosecha real, que no está "
        "disponible (D-019). Producción sigue usando determinista-v1."
    )
    return {
        "advertencia": ADVERTENCIA,
        "semilla": semilla,
        "unidad": "racimos por parcela y semana",
        "supuestos": dict(SUPUESTOS),
        "metodo_en_produccion": "determinista-v1",
        "bloques": bloques,
        "holdout": holdout,
        "decision_d003": {"predictivo_supera_a_ambos_en_holdout": supera, "texto": texto},
    }
