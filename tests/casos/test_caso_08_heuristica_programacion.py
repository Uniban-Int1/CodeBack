"""Pruebas unitarias de la heurística de programación y sus restricciones."""
from datetime import datetime

import pytest

from app.core.programacion import heuristica
from app.core.programacion.fechas import VentanaDespacho
from app.core.programacion.heuristica import (
    VERSION_METODO,
    ParcelaAProgramar,
    PlanRecoleccion,
    programar,
)
from app.core.programacion.restricciones import (
    MedioAcarreo,
    Vehiculo,
    cabe_en_vehiculo,
    viajes_necesarios,
)


@pytest.fixture
def parametros_programacion(monkeypatch):
    monkeypatch.setattr(
        heuristica,
        "parametros",
        lambda: {
            "empaque": {"minutos_por_parcela": 120},
            "planificacion": {"margen_seguridad_min": 30},
        },
    )


def ventana_normal() -> VentanaDespacho:
    return VentanaDespacho(
        inicio=datetime(2026, 10, 16, 6, 0),
        fin=datetime(2026, 10, 16, 18, 0),
    )


def parcela(
    parcela_id: str, volumen: int, minutos_acarreo: int = 60
) -> ParcelaAProgramar:
    return ParcelaAProgramar(
        parcela_id=parcela_id,
        volumen_racimos=volumen,
        minutos_acarreo=minutos_acarreo,
        medio_acarreo="cable_via",
    )


def test_programar_asigna_una_parcela_y_conserva_el_metodo(parametros_programacion):
    resultado = programar(
        [parcela("P-001", 60)],
        [Vehiculo("V1", 100)],
        ventana_normal(),
        "2026-W42",
    )

    assert resultado.periodo == "2026-W42"
    assert resultado.version_metodo == VERSION_METODO
    assert len(resultado.items) == 1
    item = resultado.items[0]
    assert item.parcela_id == "P-001"
    assert item.vehiculo_id == "V1"
    assert item.carga_estimada_racimos == 60
    assert item.cumple_ventana is True
    assert item.motivo is None


def test_programar_prioriza_fecha_limite_y_desempata_por_parcela_id(
    parametros_programacion,
):
    resultado = programar(
        [
            parcela("P-003", 10, 120),
            parcela("P-002", 10, 60),
            parcela("P-001", 10, 60),
        ],
        [Vehiculo("V1", 100)],
        ventana_normal(),
        "2026-W42",
    )

    assert [item.parcela_id for item in resultado.items] == [
        "P-003",
        "P-001",
        "P-002",
    ]
    assert [item.orden for item in resultado.items] == [1, 2, 3]
    assert [item.fecha_corte for item in resultado.items] == [
        datetime(2026, 10, 16, 13, 30),
        datetime(2026, 10, 16, 14, 30),
        datetime(2026, 10, 16, 14, 30),
    ]


def test_programar_acumula_carga_y_asigna_vehiculos_sin_exceder_capacidad(
    parametros_programacion,
):
    resultado = programar(
        [
            parcela("P-001", 50, 120),
            parcela("P-002", 60, 90),
            parcela("P-003", 30, 60),
        ],
        [Vehiculo("V2", 60), Vehiculo("V1", 100)],
        ventana_normal(),
        "2026-W42",
    )

    asignaciones = {item.parcela_id: item.vehiculo_id for item in resultado.items}
    assert asignaciones == {
        "P-001": "V1",
        "P-002": "V2",
        "P-003": "V1",
    }
    cargas = {
        vehiculo.id: sum(
            item.carga_estimada_racimos
            for item in resultado.items
            if item.vehiculo_id == vehiculo.id
        )
        for vehiculo in [Vehiculo("V1", 100), Vehiculo("V2", 60)]
    }
    assert cargas == {"V1": 80, "V2": 60}
    assert all(cargas[v.id] <= v.capacidad_racimos for v in [Vehiculo("V1", 100), Vehiculo("V2", 60)])


def test_programar_marca_no_programada_la_parcela_que_no_cabe_en_ningun_vehiculo(
    parametros_programacion,
):
    resultado = programar(
        [parcela("P-001", 70)],
        [Vehiculo("V1", 50), Vehiculo("V2", 40)],
        ventana_normal(),
        "2026-W42",
    )

    item = resultado.items[0]
    assert item.vehiculo_id is None
    assert item.cumple_ventana is False
    assert "capacidad" in (item.motivo or "").lower()
    assert item.carga_estimada_racimos == 70


def test_programar_marca_ventana_fisicamente_inalcanzable_como_no_cumplida(
    parametros_programacion,
):
    ventana = VentanaDespacho(
        inicio=datetime(2026, 10, 16, 6, 0),
        fin=datetime(2026, 10, 16, 8, 0),
    )
    resultado = programar(
        [parcela("P-001", 20, 35)],
        [Vehiculo("V1", 100)],
        ventana,
        "2026-W42",
    )

    item = resultado.items[0]
    assert item.vehiculo_id is None
    assert item.cumple_ventana is False
    assert "no caben" in (item.motivo or "").lower()


def test_programar_no_debe_presentar_como_exitosa_una_fecha_limite_vencida(
    parametros_programacion,
):
    ventana_vencida = VentanaDespacho(
        inicio=datetime(2000, 1, 1, 6, 0),
        fin=datetime(2000, 1, 1, 18, 0),
    )

    resultado = programar(
        [parcela("P-001", 20)],
        [Vehiculo("V1", 100)],
        ventana_vencida,
        "2000-W01",
    )

    item = resultado.items[0]
    assert item.vehiculo_id is None
    assert item.cumple_ventana is False
    assert item.motivo == "la fecha límite de corte ya venció"


def test_viajes_necesarios_redondea_hacia_arriba_y_cubre_cargas_no_positivas():
    medio = MedioAcarreo(
        nombre="cable_via",
        capacidad_racimos_por_viaje=65,
        minutos_por_viaje=40,
    )

    assert viajes_necesarios(130, medio) == 2
    assert viajes_necesarios(131, medio) == 3
    assert viajes_necesarios(0, medio) == 0
    assert viajes_necesarios(-1, medio) == 0


def test_viajes_necesarios_rechaza_capacidad_por_viaje_invalida():
    medio = MedioAcarreo(
        nombre="cable_via",
        capacidad_racimos_por_viaje=0,
        minutos_por_viaje=40,
    )

    with pytest.raises(ValueError, match="capacidad por viaje debe ser mayor que cero"):
        viajes_necesarios(1, medio)


@pytest.mark.parametrize(
    ("carga_actual", "carga_nueva", "esperado"),
    [(60, 40, True), (60, 41, False), (0, -1, False)],
)
def test_cabe_en_vehiculo(carga_actual, carga_nueva, esperado):
    assert cabe_en_vehiculo(carga_actual, carga_nueva, Vehiculo("V1", 100)) is esperado


def test_uso_capacidad_usa_solo_carga_asignada_y_maneja_sin_vehiculos():
    plan = PlanRecoleccion(
        periodo="2026-W42",
        items=[
            heuristica.ItemPlan("P-001", datetime(2026, 10, 16, 14), "V1", 1, 60, True),
            heuristica.ItemPlan("P-002", datetime(2026, 10, 16, 14), None, 2, 40, False),
        ],
    )

    assert plan.uso_capacidad([Vehiculo("V1", 100), Vehiculo("V2", 100)]) == 0.3
    assert plan.uso_capacidad([]) == 0.0
    assert PlanRecoleccion(periodo="2026-W42").uso_capacidad(
        [Vehiculo("V1", 0)]
    ) == 0.0
