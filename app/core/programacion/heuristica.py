"""EL NÚCLEO DEL SUBPROYECTO — heurística de programación de recolección y transporte.

Los cuatro pasos:

    1. Para cada parcela: fecha_limite = ventana - tiempo_empaque - tiempo_acarreo
    2. Ordenar parcelas por fecha_limite (la más urgente primero)
    3. Asignar carga a los vehículos disponibles hasta agotar capacidad
    4. Reasignar lo que no alcanza su ventana

Deliberadamente NO es un solucionador exacto de ruteo. Ver D-002 en DECISIONES.md.

Criterio de validación: sobre instancias pequeñas de solución conocida, el plan debe
respetar capacidad y ventana en el 100 % de los casos.

Responsable: Lizbeth — frente backend (T-10)
"""
from dataclasses import dataclass, field
from datetime import datetime

from app.core.programacion.restricciones import Vehiculo

VERSION_METODO = "heuristica-v1"


@dataclass(frozen=True)
class ParcelaAProgramar:
    parcela_id: str
    volumen_racimos: int
    minutos_acarreo: int
    medio_acarreo: str


@dataclass
class ItemPlan:
    parcela_id: str
    fecha_corte: datetime
    vehiculo_id: str | None
    orden: int
    carga_estimada_racimos: int
    cumple_ventana: bool
    motivo: str | None = None          # por qué no cumple, cuando aplica


@dataclass
class PlanRecoleccion:
    periodo: str
    version_metodo: str = VERSION_METODO
    items: list[ItemPlan] = field(default_factory=list)

    @property
    def cumplimiento_ventana(self) -> float:
        """Métrica de validación: % de parcelas que alcanzan su ventana."""
        if not self.items:
            return 0.0
        return sum(i.cumple_ventana for i in self.items) / len(self.items)

    def uso_capacidad(self, vehiculos: list[Vehiculo]) -> float:
        """Métrica de validación: carga asignada / capacidad disponible."""
        raise NotImplementedError("T-10")


def programar(
    parcelas: list[ParcelaAProgramar],
    vehiculos: list[Vehiculo],
    ventana,                      # VentanaDespacho
    periodo: str,
) -> PlanRecoleccion:
    """Genera el plan de recolección y transporte del periodo."""
    raise NotImplementedError("T-10")
