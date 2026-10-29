#!/usr/bin/env python3
"""Evalúa en vivo el modelo predictivo frente al determinista y la línea base ingenua.

Uso:  python scripts/evaluar_modelos.py [semilla]

Usa el escenario SINTÉTICO de app/core/proyeccion/escenario_sintetico.py (D-006, D-019):
la "cosecha real" es simulada, así que el resultado valida el pipeline, no el campo.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.proyeccion.escenario_sintetico import evaluar_escenario_sintetico  # noqa: E402


def main() -> None:
    semilla = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    r = evaluar_escenario_sintetico(semilla)

    print("=" * 78)
    print(" EVALUACIÓN TEMPORAL DE MODELOS DE PROYECCIÓN (T-14, D-003)")
    print("=" * 78)
    print(f" ⚠  {r['advertencia']}")
    s = r["supuestos"]
    print(
        f"\n Escenario: {s['parcelas']} parcelas × {s['semanas']} semanas · semilla {r['semilla']}\n"
        f" Supuestos de la 'cosecha real' simulada: ciclo {s['ciclo_real_semanas']} sem "
        f"(la fórmula asume 10.5), estacionalidad ±{s['amplitud_estacional']:.0%}, "
        f"ruido {s['ruido_relativo']:.0%}"
    )
    print(f" Validación: {s['num_folds']} folds expansivos + holdout final de {s['num_periodos_holdout']} semana")
    print(f" Unidad del MAE: {r['unidad']}\n")

    print(f" {'Bloque':<9} {'Semanas evaluadas':<28} {'n':>3} {'Predictivo':>11} {'Determinista':>13} {'Ingenua':>9}")
    print(" " + "-" * 76)
    for b in r["bloques"] + [r["holdout"]]:
        semanas = ", ".join(b["periodos_evaluacion"])
        print(
            f" {b['bloque']:<9} {semanas:<28} {b['n_comparadas']:>3} "
            f"{b['mae_predictivo']:>11.2f} {b['mae_determinista']:>13.2f} {b['mae_ingenua']:>9.2f}"
        )
    print("\n Decisión D-003 (sobre el holdout):")
    print(f"  {r['decision_d003']['texto']}")
    print(f"  Método en producción: {r['metodo_en_produccion']}\n")


if __name__ == "__main__":
    main()
