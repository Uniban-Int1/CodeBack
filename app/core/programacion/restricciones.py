"""Restricciones del plan: capacidad de acarreo y de vehículo, y ventana de despacho.

Responsable: Lizbeth — frente backend (T-10)
"""
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
    raise NotImplementedError("T-10")


def cabe_en_vehiculo(carga_actual: int, carga_nueva: int, vehiculo: Vehiculo) -> bool:
    raise NotImplementedError("T-10")
