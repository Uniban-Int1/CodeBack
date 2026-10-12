"""Casos de integración del servicio de recomendación de insumos."""
from datetime import datetime

import pytest
import yaml

from app.core.programacion.fechas import VentanaDespacho, VentanaInalcanzable
from app.core.proyeccion.base import Aforamiento
from app.core.servicio import (
    ParcelaExcluida,
    RecomendacionInsumos,
    recomendar_insumos,
    separar_aforamientos,
)


def parametros_simulados(coeficiente_cajas: float = 0.85) -> dict:
    """Parámetros de dominio inyectables para los casos conocidos."""
    return {
        "acarreo": {"cable_via": {"minutos_por_viaje": 35}},
        "empaque": {"minutos_por_parcela": 120},
        "planificacion": {"margen_seguridad_min": 30},
        "proyeccion": {"ciclo_racimo_semanas": 5, "factor_perdida": 0},
        "consumo_unitario": {
            "cajas": coeficiente_cajas,
            "carton": 0.85,
            "bolsas": 1.0,
        },
    }


def aforamiento_conocido() -> Aforamiento:
    """Aforamiento de 100 plantas con confianza completa para los casos conocidos."""
    return Aforamiento("P-100", 100, 1.0, 1.0)


def ventana_conocida() -> VentanaDespacho:
    """Ventana usada en los cálculos manuales de los casos conocidos."""
    return VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 16, 0),
    )


def test_recomendar_insumos_e2e_con_parametros_simulados():
    """Caso 04 — recomendación completa con diccionario de parámetros simulado.

    Entradas:
        100 plantas, confianza 1.0, ciclo 5, pérdida 0; acarreo 35 min.
        coeficientes cajas/carton/bolsas: 0.85/0.85/1.0; inventario: 10/5/15.

    Cálculo a mano:
        volumen = 100 * (1 / 5) * 1.0 * (1 - 0) = 20.0.
        holgura = 120 + 35 + 30 = 185 min; 16:00 - 185 min = 12:55.
        requeridos = 20 * (0.85/0.85/1.0) = 17.0/17.0/20.0.
        déficits = 17.0 - 10, 17.0 - 5, 20.0 - 15 = 7.0/12.0/5.0.

    Resultado esperado: volumen 20.0, fecha 2026-09-21 12:55 y déficits 7.0/12.0/5.0.
    """
    resultado = recomendar_insumos(
        aforamiento=aforamiento_conocido(),
        ventana=ventana_conocida(),
        inventario={"cajas": 10, "carton": 5, "bolsas": 15},
        periodo="2026-W38",
        minutos_acarreo=35,
        params=parametros_simulados(),
    )
    por_insumo = {item.insumo: item for item in resultado.requerimientos}

    assert resultado.volumen_racimos == pytest.approx(20.0)
    assert resultado.fecha_limite_corte == datetime(2026, 9, 21, 12, 55)
    assert por_insumo["cajas"].cantidad_requerida == pytest.approx(17.0)
    assert por_insumo["cajas"].deficit == pytest.approx(7.0)
    assert por_insumo["carton"].cantidad_requerida == pytest.approx(17.0)
    assert por_insumo["carton"].deficit == pytest.approx(12.0)
    assert por_insumo["bolsas"].cantidad_requerida == pytest.approx(20.0)
    assert por_insumo["bolsas"].deficit == pytest.approx(5.0)


def test_recomendar_insumos_acepta_parametros_cargados_desde_yaml_temporal(tmp_path):
    """Caso 04b — la inyección desde YAML modifica el requerido proporcionalmente.

    Entradas:
        volumen proyectado: 20.0; YAML inicial con coeficiente cajas 0.85;
        YAML modificado con coeficiente cajas 0.50; inventario cajas: 0.

    Cálculo a mano:
        con 0.85, requerida = 20.0 * 0.85 = 17.0.
        con 0.50, requerida = 20.0 * 0.50 = 10.0.
        10.0 = 17.0 * (0.50 / 0.85), por lo que el cambio es proporcional.

    Resultado esperado: cajas cambia de 17.0 a 10.0 al cargar el YAML modificado.
    """
    ruta = tmp_path / "parametros.yaml"
    with ruta.open("w", encoding="utf-8") as archivo:
        yaml.safe_dump(parametros_simulados(), archivo)
    with ruta.open(encoding="utf-8") as archivo:
        params_iniciales = yaml.safe_load(archivo)

    inicial = recomendar_insumos(
        aforamiento_conocido(),
        ventana_conocida(),
        {"cajas": 0, "carton": 0, "bolsas": 0},
        "2026-W38",
        minutos_acarreo=35,
        params=params_iniciales,
    )

    params_modificados = parametros_simulados(coeficiente_cajas=0.50)
    with ruta.open("w", encoding="utf-8") as archivo:
        yaml.safe_dump(params_modificados, archivo)
    with ruta.open(encoding="utf-8") as archivo:
        params_modificados = yaml.safe_load(archivo)

    modificado = recomendar_insumos(
        aforamiento_conocido(),
        ventana_conocida(),
        {"cajas": 0, "carton": 0, "bolsas": 0},
        "2026-W38",
        minutos_acarreo=35,
        params=params_modificados,
    )
    requerido_inicial = {item.insumo: item for item in inicial.requerimientos}["cajas"]
    requerido_modificado = {
        item.insumo: item for item in modificado.requerimientos
    }["cajas"]

    assert requerido_inicial.cantidad_requerida == pytest.approx(17.0)
    assert requerido_modificado.cantidad_requerida == pytest.approx(10.0)
    assert requerido_modificado.cantidad_requerida == pytest.approx(
        requerido_inicial.cantidad_requerida * (0.50 / 0.85)
    )


def test_recomendar_insumos_carga_parametros_reales_si_no_se_inyectan():
    """Caso 04c — carga del YAML real cuando params es None.

    Entradas:
        aforamiento de 100 plantas, ventana 06:00 a 16:00, inventario cero,
        acarreo 35 min y params=None.

    Cálculo a mano:
        params=None indica que el servicio debe cargar config/parametros.yaml.
        El YAML real define tres coeficientes: cajas, carton y bolsas.

    Resultado esperado: RecomendacionInsumos con tres requerimientos y método no vacío.
    """
    resultado = recomendar_insumos(
        aforamiento=aforamiento_conocido(),
        ventana=ventana_conocida(),
        inventario={"cajas": 0, "carton": 0, "bolsas": 0},
        periodo="2026-W38",
        minutos_acarreo=35,
    )

    assert isinstance(resultado, RecomendacionInsumos)
    assert {item.insumo for item in resultado.requerimientos} == {
        "cajas",
        "carton",
        "bolsas",
    }
    assert resultado.version_metodo


def test_recomendar_insumos_propaga_ventana_inalcanzable():
    """Caso 04d — acarreo mayor que una ventana de dos horas.

    Entradas:
        ventana 06:00 a 08:00 (120 min), empaque 120 min, margen 30 min,
        acarreo 121 min y parámetros simulados.

    Cálculo a mano:
        holgura = 120 + 121 + 30 = 271 min.
        08:00 - 271 min = 03:29, anterior al inicio de ventana (06:00).

    Resultado esperado: VentanaInalcanzable propagada por el servicio.
    """
    ventana = VentanaDespacho(
        inicio=datetime(2026, 9, 21, 6, 0),
        fin=datetime(2026, 9, 21, 8, 0),
    )

    with pytest.raises(VentanaInalcanzable):
        recomendar_insumos(
            aforamiento=aforamiento_conocido(),
            ventana=ventana,
            inventario={"cajas": 10, "carton": 5, "bolsas": 15},
            periodo="2026-W38",
            minutos_acarreo=121,
            params=parametros_simulados(),
        )


def test_separar_aforamientos_registra_parcela_sin_aforamiento():
    disponibles, excluidas = separar_aforamientos(["P-101"], [])

    assert disponibles == []
    assert len(excluidas) == 1
    assert isinstance(excluidas[0], ParcelaExcluida)
    assert excluidas[0].parcela_id == "P-101"
    assert excluidas[0].motivo == "sin_aforamiento"


def test_separar_aforamientos_conserva_parcela_valida_en_entrada_mixta():
    aforamiento = aforamiento_conocido()

    disponibles, excluidas = separar_aforamientos(
        ["P-101", aforamiento.parcela_id],
        [aforamiento],
    )

    assert disponibles == [aforamiento]
    assert disponibles[0] is aforamiento
    assert [(item.parcela_id, item.motivo) for item in excluidas] == [
        ("P-101", "sin_aforamiento")
    ]
