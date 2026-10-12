"""Escenario T-19 sintético; no representa datos históricos de Unibán.

Entradas invariantes en ambas ejecuciones:
    sintetico_parcela: P-SINTETICA, 60 racimos, 60 minutos de acarreo.
    sintetico_vehiculo: V1, capacidad de 100 racimos.
    sintetico_empaque: 120 minutos; margen de seguridad: 30 minutos.
    sintetico_periodo: semana ISO de la fecha inicial de la ventana, compartida
    entre los dos planes.

Único cambio: la primera ventana va de las 06:00 a las 12:00; la segunda se
desplaza a las 09:30 y conserva el cierre a las 12:00.

Cálculo manual:
    holgura requerida = 120 + 60 + 30 = 210 minutos (3 h 30 min).
    Antes: 12:00 - 3 h 30 min = 08:30, dentro de la ventana; se asignan 60 de
    100 racimos. Cumplimiento = 1/1 = 1.0; uso = 60/100 = 0.6.
    Después: entre 09:30 y 12:00 solo hay 2 h 30 min. La ventana es
    físicamente inalcanzable; no se asigna vehículo. Cumplimiento = 0/1 = 0.0;
    uso = 0/100 = 0.0.

Interpretación: el plan explícitamente generado para la ventana posterior
registra la parcela como no programada con el motivo de ventana inalcanzable.
Las dos llamadas comparan escenarios sintéticos; no recalculan automáticamente
un plan operativo existente ni implican que la heurística sea óptima.
"""
from datetime import datetime, timedelta

from app.core.programacion.fechas import VentanaDespacho
from app.core.programacion.heuristica import ParcelaAProgramar, programar
from app.core.programacion.restricciones import Vehiculo


def test_t19_compara_planes_sinteticos_antes_y_despues_de_mover_ventana():
    inicio_dia = datetime(2099, 11, 11)
    ventana_antes = VentanaDespacho(
        inicio=inicio_dia.replace(hour=6),
        fin=inicio_dia.replace(hour=12),
    )
    ventana_despues = VentanaDespacho(
        inicio=inicio_dia.replace(hour=9, minute=30),
        fin=inicio_dia.replace(hour=12),
    )
    parcelas = [
        ParcelaAProgramar(
            parcela_id="P-SINTETICA",
            volumen_racimos=60,
            minutos_acarreo=60,
            medio_acarreo="cable_via",
        )
    ]
    vehiculos = [Vehiculo(id="V1", capacidad_racimos=100)]
    semana_iso = ventana_antes.inicio.isocalendar()
    periodo = f"{semana_iso.year}-W{semana_iso.week:02d}"
    parametros = {
        "minutos_empaque": 120,
        "margen_seguridad_min": 30,
    }

    plan_antes = programar(
        parcelas,
        vehiculos,
        ventana_antes,
        periodo,
        **parametros,
    )
    plan_despues = programar(
        parcelas,
        vehiculos,
        ventana_despues,
        periodo,
        **parametros,
    )

    item_antes = plan_antes.items[0]
    item_despues = plan_despues.items[0]
    assert plan_antes.periodo == plan_despues.periodo == periodo
    assert item_antes.parcela_id == item_despues.parcela_id == "P-SINTETICA"

    assert item_antes.vehiculo_id == "V1"
    assert item_antes.fecha_corte == ventana_antes.fin - timedelta(minutes=210)
    assert item_antes.cumple_ventana is True
    assert item_antes.motivo is None
    assert plan_antes.cumplimiento_ventana == 1.0
    assert plan_antes.uso_capacidad(vehiculos) == 0.6

    assert item_despues.vehiculo_id is None
    assert item_despues.fecha_corte == ventana_despues.fin
    assert item_despues.cumple_ventana is False
    assert "no caben" in (item_despues.motivo or "").lower()
    assert plan_despues.cumplimiento_ventana == 0.0
    assert plan_despues.uso_capacidad(vehiculos) == 0.0

    for ventana, plan in (
        (ventana_antes, plan_antes),
        (ventana_despues, plan_despues),
    ):
        cargas_por_vehiculo = {
            vehiculo.id: sum(
                item.carga_estimada_racimos
                for item in plan.items
                if item.vehiculo_id == vehiculo.id
            )
            for vehiculo in vehiculos
        }
        assert all(
            cargas_por_vehiculo[vehiculo.id] <= vehiculo.capacidad_racimos
            for vehiculo in vehiculos
        )
        assert all(
            item.vehiculo_id is not None and item.cumple_ventana
            for item in plan.items
            if item.vehiculo_id is not None
        )
        assert all(
            not item.cumple_ventana
            and item.vehiculo_id is None
            and item.motivo
            for item in plan.items
            if item.vehiculo_id is None
        )
        assert all(
            ventana.inicio <= item.fecha_corte <= ventana.fin
            for item in plan.items
            if item.cumple_ventana
        )
