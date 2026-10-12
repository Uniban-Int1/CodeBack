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

from app.config import parametros
from app.core.programacion.fechas import VentanaInalcanzable, fecha_limite_corte
from app.core.programacion.restricciones import Vehiculo, cabe_en_vehiculo

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
        if not vehiculos:
            return 0.0
        capacidad_total = sum(v.capacidad_racimos for v in vehiculos)
        carga_total = sum(
            item.carga_estimada_racimos for item in self.items if item.vehiculo_id is not None
        )
        if capacidad_total == 0:
            return 0.0
        return carga_total / capacidad_total


def programar(
    parcelas: list[ParcelaAProgramar],
    vehiculos: list[Vehiculo],
    ventana,                      # VentanaDespacho
    periodo: str,
) -> PlanRecoleccion:
    """Genera el plan de recolección y transporte del periodo."""
    params = parametros()
    minutos_empaque = int(params["empaque"]["minutos_por_parcela"])
    margen_seguridad_min = int(params["planificacion"]["margen_seguridad_min"])

    cargas_por_vehiculo = {vehiculo.id: 0 for vehiculo in vehiculos}
    parcelas_ordenadas: list[tuple[datetime, ParcelaAProgramar]] = []

    for parcela in parcelas:
        try:
            fecha_corte = fecha_limite_corte(
                ventana,
                minutos_empaque=minutos_empaque,
                minutos_acarreo=parcela.minutos_acarreo,
                margen_seguridad_min=margen_seguridad_min,
            )
        except VentanaInalcanzable:
            fecha_corte = ventana.fin
        parcelas_ordenadas.append((fecha_corte, parcela))

    items: list[ItemPlan] = []
    for orden, (fecha_corte, parcela) in enumerate(
        sorted(parcelas_ordenadas, key=lambda entrada: (entrada[0], entrada[1].parcela_id)),
        start=1,
    ):
        try:
            fecha_limite = fecha_limite_corte(
                ventana,
                minutos_empaque=minutos_empaque,
                minutos_acarreo=parcela.minutos_acarreo,
                margen_seguridad_min=margen_seguridad_min,
            )
        except VentanaInalcanzable as exc:
            items.append(
                ItemPlan(
                    parcela_id=parcela.parcela_id,
                    fecha_corte=fecha_corte,
                    vehiculo_id=None,
                    orden=orden,
                    carga_estimada_racimos=parcela.volumen_racimos,
                    cumple_ventana=False,
                    motivo=str(exc),
                )
            )
            continue

        if fecha_limite < datetime.now():
            items.append(
                ItemPlan(
                    parcela_id=parcela.parcela_id,
                    fecha_corte=fecha_limite,
                    vehiculo_id=None,
                    orden=orden,
                    carga_estimada_racimos=parcela.volumen_racimos,
                    cumple_ventana=False,
                    motivo="la fecha límite de corte ya venció",
                )
            )
            continue

        vehiculo_asignado: Vehiculo | None = None
        for vehiculo in sorted(vehiculos, key=lambda current: current.id):
            carga_actual = cargas_por_vehiculo.get(vehiculo.id, 0)
            if cabe_en_vehiculo(carga_actual, parcela.volumen_racimos, vehiculo):
                cargas_por_vehiculo[vehiculo.id] = carga_actual + parcela.volumen_racimos
                vehiculo_asignado = vehiculo
                break

        if vehiculo_asignado is None:
            items.append(
                ItemPlan(
                    parcela_id=parcela.parcela_id,
                    fecha_corte=fecha_limite,
                    vehiculo_id=None,
                    orden=orden,
                    carga_estimada_racimos=parcela.volumen_racimos,
                    cumple_ventana=False,
                    motivo=(
                        f"la carga ({parcela.volumen_racimos} racimos) supera la capacidad "
                        "de todos los vehículos disponibles"
                    ),
                )
            )
            continue

        items.append(
            ItemPlan(
                parcela_id=parcela.parcela_id,
                fecha_corte=fecha_limite,
                vehiculo_id=vehiculo_asignado.id,
                orden=orden,
                carga_estimada_racimos=parcela.volumen_racimos,
                cumple_ventana=True,
                motivo=None,
            )
        )

    return PlanRecoleccion(periodo=periodo, version_metodo=VERSION_METODO, items=items)
