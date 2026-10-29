#!/usr/bin/env python3
"""Demo de programación de cosecha y despacho con varios productores (T-10).

Uso:  python scripts/demo_programacion.py [hora_fin_ventana]     p. ej. 16:00 o 11:00

Proyecta la cosecha de cada parcela, calcula su hora límite de corte, las ordena por
urgencia, consolida la carga en los vehículos disponibles y deriva los insumos del
volumen programado. Datos SINTÉTICOS de ejemplo (D-006, D-019).
"""
from datetime import date, datetime, time, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import parametros  # noqa: E402
from app.core.insumos.estimacion import estimar  # noqa: E402
from app.core.programacion.fechas import VentanaDespacho  # noqa: E402
from app.core.programacion.heuristica import ParcelaAProgramar, programar  # noqa: E402
from app.core.programacion.restricciones import Vehiculo  # noqa: E402
from app.core.proyeccion.base import Aforamiento, proyectar  # noqa: E402

# (parcela, productor, plantas aforadas, confianza, minutos de acarreo, medio)
PARCELAS_SINTETICAS = [
    ("P-SIN-01", "Productor A", 1850, 0.87, 35, "cable_via"),
    ("P-SIN-02", "Productor A", 2400, 0.90, 50, "cable_via"),
    ("P-SIN-03", "Productor B", 1500, 0.82, 90, "traccion_animal"),
    ("P-SIN-04", "Productor C", 3200, 0.88, 40, "cable_via"),
    ("P-SIN-05", "Productor D", 900, 0.80, 120, "traccion_animal"),
]
VEHICULOS = [Vehiculo("V-1", 300), Vehiculo("V-2", 250)]
INVENTARIO = {"cajas": 300.0, "carton": 250.0, "bolsas": 500.0}


def semana_iso(dia: date) -> str:
    anio, semana, _ = dia.isocalendar()
    return f"{anio}-W{semana:02d}"


def main() -> None:
    params = parametros()
    fin_txt = sys.argv[1] if len(sys.argv) > 1 else "16:00"
    h, m = (int(x) for x in fin_txt.split(":"))
    manana = date.today() + timedelta(days=1)
    ventana = VentanaDespacho(datetime.combine(manana, time(6, 0)), datetime.combine(manana, time(h, m)))
    periodo = semana_iso(manana)

    print("=" * 84)
    print(" PROGRAMACIÓN DE COSECHA Y DESPACHO — varios productores (T-10)")
    print("=" * 84)
    print(" ⚠  Datos sintéticos de ejemplo, no registros de Unibán (D-006, D-019).")
    print(f" Ventana de despacho: {ventana.inicio:%Y-%m-%d %H:%M} a {ventana.fin:%H:%M} · periodo {periodo}")
    print(" Vehículos: " + ", ".join(f"{v.id} ({v.capacidad_racimos} racimos)" for v in VEHICULOS))

    print("\n 1) Proyección de cosecha por parcela (determinista-v1)")
    productores, parcelas = {}, []
    for pid, productor, plantas, conf, acarreo, medio in PARCELAS_SINTETICAS:
        vol = proyectar(
            Aforamiento(pid, plantas, 0.0, conf), periodo=periodo,
            ciclo_racimo_semanas=params["proyeccion"]["ciclo_racimo_semanas"],
            factor_perdida=params["proyeccion"]["factor_perdida"],
        ).volumen_racimos
        productores[pid] = productor
        parcelas.append(ParcelaAProgramar(pid, round(vol), acarreo, medio))
        print(f"    {pid} ({productor}): {plantas} plantas, confianza {conf} → {round(vol)} racimos · acarreo {acarreo} min")

    plan = programar(
        parcelas, VEHICULOS, ventana, periodo,
        minutos_empaque=params["empaque"]["minutos_por_parcela"],
        margen_seguridad_min=params["planificacion"]["margen_seguridad_min"],
    )

    print("\n 2) Plan: orden por urgencia y consolidación en vehículos")
    print(f"    {'Orden':<6}{'Parcela':<10}{'Productor':<13}{'Corte límite':<14}{'Vehículo':<10}{'Carga':>6}  Estado")
    for it in plan.items:
        estado = "cumple ventana" if it.cumple_ventana else f"NO programada: {it.motivo}"
        print(
            f"    {it.orden:<6}{it.parcela_id:<10}{productores[it.parcela_id]:<13}"
            f"{it.fecha_corte:%H:%M}{'':<9}{it.vehiculo_id or '—':<10}{it.carga_estimada_racimos:>6}  {estado}"
        )
    for v in VEHICULOS:
        carga = sum(i.carga_estimada_racimos for i in plan.items if i.vehiculo_id == v.id)
        juntos = sorted({productores[i.parcela_id] for i in plan.items if i.vehiculo_id == v.id})
        print(f"    {v.id}: {carga}/{v.capacidad_racimos} racimos · consolida: {', '.join(juntos) or 'nada'}")

    volumen_programado = sum(i.carga_estimada_racimos for i in plan.items if i.vehiculo_id)
    print(f"\n 3) Insumos para el volumen programado ({volumen_programado} racimos)")
    for r in estimar(volumen_programado, manana, params["consumo_unitario"], INVENTARIO):
        print(
            f"    {r.insumo:<7} requerido {r.cantidad_requerida:>8.2f} · inventario {r.inventario_disponible:>6.0f}"
            f" · déficit {r.deficit:>7.2f} · excedente {r.excedente:>7.2f}"
        )

    print("\n 4) Métricas del plan")
    print(f"    Cumplimiento de ventana: {plan.cumplimiento_ventana:.0%}")
    print(f"    Uso de capacidad:        {plan.uso_capacidad(VEHICULOS):.0%}")
    print(f"    Método trazable:         {plan.version_metodo}\n")


if __name__ == "__main__":
    main()
