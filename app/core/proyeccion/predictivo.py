"""Modelo predictivo de proyección de cosecha (scikit-learn).

Partición temporal y validación cruzada de series de tiempo.
Variables: edad de racimo (8-13 semanas), aforamiento, estacionalidad, consumos observados.

REGLA (D-003): este modelo solo se adopta si supera de forma medible al modelo base
Y a una línea base ingenua. Si no lo supera, se conserva el determinista y se
documenta la razón en DECISIONES.md. Eso no es un fracaso: es el resultado.

Responsable: Camilo — frente backend (T-14)
"""
METODO = "predictivo-v1"


def entrenar(df, **params):
    """Entrena y devuelve el modelo junto con sus métricas."""
    raise NotImplementedError("T-14")


def predecir(modelo, X):
    raise NotImplementedError("T-14")
