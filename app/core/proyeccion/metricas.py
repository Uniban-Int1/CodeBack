"""Métricas de evaluación de la proyección.

Incluye obligatoriamente la comparación contra una línea base ingenua
(seasonal naive / media histórica), sin la cual no se puede afirmar que el
modelo predictivo sirvió. Hyndman y Athanasopoulos (2021).

Responsable: Camilo — frente backend (T-14, T-20)
"""


def linea_base_ingenua(serie):
    """Seasonal naive: el valor de la semana anterior."""
    raise NotImplementedError("T-14")


def mae(y_real, y_pred):
    raise NotImplementedError("T-14")


def comparar(y_real, y_pred_modelo, y_pred_base, y_pred_ingenua) -> dict:
    """Devuelve la tabla comparativa que decide si el modelo se adopta."""
    raise NotImplementedError("T-14")
