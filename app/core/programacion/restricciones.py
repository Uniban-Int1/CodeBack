"""Restricciones del plan: capacidad de acarreo y de vehículo, y ventana de despacho.

Responsable: Lizbeth — frente backend (T-10)
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vehiculo:
    id: str
    capacidad_racimos: int


@dataclass(frozen=True)
class MedioAcarreo:
    nombre: str                    # "cable_via" | "traccion_animal"
    capacidad_racimos_por_viaje: int
    minutos_por_viaje: int


def viajes_necesarios(racimos: int, medio: MedioAcarreo) -> int:
    """Cuántos viajes de acarreo hacen falta para mover esa cantidad de racimos."""
    if racimos <= 0:
        return 0
    if medio.capacidad_racimos_por_viaje <= 0:
        raise ValueError("La capacidad por viaje debe ser mayor que cero.")
    return math.ceil(racimos / medio.capacidad_racimos_por_viaje)


def cabe_en_vehiculo(carga_actual: int, carga_nueva: int, vehiculo: Vehiculo) -> bool:
    if carga_nueva < 0:
        return False
    return carga_actual + carga_nueva <= vehiculo.capacidad_racimos
