#!/usr/bin/env python3
"""Script interactivo de demostración para sustentación de Proyecto Integrador I.

Demostración obligatoria (29 de octubre):
1. Partiendo de un productor y parcela (P-018), ejecutar con valores conocidos.
2. Generar automáticamente recomendación de insumos y programación logística.
3. Modificar en vivo variables de entrada (ej. ventana de despacho o inventario)
   y evidenciar el recálculo inmediato y trazable.
"""
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Asegurar importación del paquete app desde la raíz
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.programacion.fechas import VentanaDespacho
from app.core.proyeccion.base import Aforamiento
from app.core.servicio import recomendar_insumos


def imprimir_encabezado():
    print("=" * 72)
    print(" 🍌 SISTEMA DE APOYO A DECISIONES — PLÁTANO / UNIBÁN (EQUIPO 2)")
    print("    Demostración en vivo de Proyección, Logística e Insumos")
    print("=" * 72)


def mostrar_resultado(titulo: str, rec, ventana: VentanaDespacho, inv_cajas: float):
    print(f"\n👉 {titulo}")
    print("-" * 72)
    print(f" • Parcela: {rec.parcela_id} | Periodo: {rec.periodo}")
    print(f" • Cosecha Proyectada: {rec.volumen_racimos} racimos")
    print(f" • Ventana de Despacho (Embarque): {ventana.inicio.strftime('%Y-%m-%d %H:%M')} a {ventana.fin.strftime('%H:%M')}")
    print(f" • Fecha/Hora Límite de Corte:     {rec.fecha_limite_corte.strftime('%Y-%m-%d %H:%M')}")
    print(f" • Método Trazable (D-005):        {rec.version_metodo}")
    print("\n   [Requerimientos de Insumos de Empaque]:")
    print(f"   {'Insumo':<10} | {'Requerido':<10} | {'Inventario':<10} | {'Déficit':<10} | {'Estado'}")
    print("   " + "-" * 62)
    for req in rec.requerimientos:
        estado = "⚠️ FALTANTE" if req.deficit > 0 else "✓ ABASTECIDO"
        print(f"   {req.insumo:<10} | {req.cantidad_requerida:<10.1f} | {req.inventario_disponible:<10.1f} | {req.deficit:<10.1f} | {estado}")
    print("-" * 72)


def main():
    imprimir_encabezado()

    # Caso Base Conocido (según fixtures del contrato v1)
    parcela_id = "P-018"
    periodo = "2026-W38"
    plantas_inicial = 1850
    confianza_inicial = 0.87
    area_ha = 2.4
    minutos_acarreo = 35 # Cable vía

    ventana_base = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )
    inventario_base = {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0}

    print("\n1️⃣  EJECUCIÓN DEL CASO BASE CONOCIDO")
    print(f"   • Parcela: {parcela_id} ({plantas_inicial} plantas censadas, confianza: {confianza_inicial})")
    print(f"   • Ventana de embarque: {ventana_base.inicio} a {ventana_base.fin}")
    print(f"   • Inventario actual de cajas: {inventario_base['cajas']} unidades")

    aforamiento = Aforamiento(
        parcela_id=parcela_id,
        num_plantas=plantas_inicial,
        area_ha=area_ha,
        calidad_confianza=confianza_inicial,
    )

    rec_base = recomendar_insumos(
        aforamiento=aforamiento,
        ventana=ventana_base,
        inventario=inventario_base,
        periodo=periodo,
        minutos_acarreo=minutos_acarreo,
    )

    mostrar_resultado("RESULTADO CASO BASE", rec_base, ventana_base, inventario_base["cajas"])

    # Demostración en vivo de cambio de variables
    print("\n2️⃣  DEMOSTRACIÓN INTERACTIVA DE VARIACIÓN DE VARIABLES")
    print("   (Exigido: modificar alguna variable de entrada y evidenciar el recálculo)")
    print("\nOpciones de prueba rápida:")
    print("  [1] Simular RETRASO/CAMBIO DE VENTANA DE DESPACHO (adelantar cierre a las 13:00)")
    print("  [2] Simular AUMENTO DE INVENTARIO (subir stock de cajas a 500 para cubrir déficit)")
    print("  [3] Simular INCREMENTO DE PRODUCCIÓN (subir plantas aforadas a 2,500 matas)")
    print("  [4] Ingresar valores personalizados manualmente")

    try:
        opcion = input("\nSeleccione una opción (1-4) [default: 1]: ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        opcion = "1"

    ventana_mod = ventana_base
    inventario_mod = dict(inventario_base)
    aforamiento_mod = aforamiento

    if opcion == "1":
        # Adelanto o cierre temprano de la ventana
        nueva_fin = datetime(2026, 9, 21, 13, 0)
        ventana_mod = VentanaDespacho(inicio=ventana_base.inicio, fin=nueva_fin)
        print(f"\n🔄 Modificando: Cierre de ventana pasa de 16:00 a las {nueva_fin.strftime('%H:%M')} hrs.")
    elif opcion == "2":
        inventario_mod["cajas"] = 500.0
        print(f"\n🔄 Modificando: Inventario de cajas pasa de 300 a {inventario_mod['cajas']} unidades.")
    elif opcion == "3":
        nuevas_plantas = 2500
        aforamiento_mod = Aforamiento(
            parcela_id=parcela_id,
            num_plantas=nuevas_plantas,
            area_ha=area_ha,
            calidad_confianza=confianza_inicial,
        )
        print(f"\n🔄 Modificando: Plantas censadas pasan de 1,850 a {nuevas_plantas} plantas.")
    elif opcion == "4":
        try:
            p = int(input("Número de plantas: ") or plantas_inicial)
            c = float(input("Inventario de cajas: ") or inventario_base["cajas"])
            h = int(input("Hora de fin de ventana (ej. 14 para 14:00): ") or 16)
            aforamiento_mod = Aforamiento(
                parcela_id=parcela_id,
                num_plantas=p,
                area_ha=area_ha,
                calidad_confianza=confianza_inicial,
            )
            inventario_mod["cajas"] = c
            ventana_mod = VentanaDespacho(inicio=ventana_base.inicio, fin=datetime(2026, 9, 21, h, 0))
        except ValueError:
            print("Entrada inválida, usando opción 1 por defecto.")
            ventana_mod = VentanaDespacho(inicio=ventana_base.inicio, fin=datetime(2026, 9, 21, 13, 0))

    # Recalcular automáticamente
    rec_mod = recomendar_insumos(
        aforamiento=aforamiento_mod,
        ventana=ventana_mod,
        inventario=inventario_mod,
        periodo=periodo,
        minutos_acarreo=minutos_acarreo,
    )

    mostrar_resultado("RESULTADO TRAS LA MODIFICACIÓN EN VIVO", rec_mod, ventana_mod, inventario_mod["cajas"])

    print("\n✅ CONCLUSIÓN DE LA DEMOSTRACIÓN:")
    if ventana_mod != ventana_base:
        diff_min = int((rec_base.fecha_limite_corte - rec_mod.fecha_limite_corte).total_seconds() / 60)
        print(f" • La fecha límite de corte se adelantó automáticamente {diff_min} minutos para proteger el embarque.")
    if inventario_mod["cajas"] != inventario_base["cajas"]:
        print(f" • El déficit de cajas se recalculó inmediatamente frente al nuevo stock.")
    print(" • Toda la operación respeta la decisión D-005 con trazabilidad de método.\n")


if __name__ == "__main__":
    main()
