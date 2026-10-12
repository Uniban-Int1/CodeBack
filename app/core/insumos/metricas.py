"""Métricas técnicas de estimación de insumos.

Los resultados requieren unidades y periodos explícitos; las unidades de ejemplo
en pruebas sintéticas no representan unidades confirmadas de Unibán.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from math import isfinite
from numbers import Real
import re
from typing import Literal


EstadoComparacion = Literal["evaluable", "consumo_ausente", "no_comparable"]
LadoRegistro = Literal["estimacion", "consumo"]


@dataclass(frozen=True)
class EstimacionInsumo:
    insumo: str | None
    parcela_id: str | None
    periodo: str | None
    cantidad_requerida: Real
    unidad: str | None


@dataclass(frozen=True)
class ConsumoObservado:
    insumo: str | None
    parcela_id: str | None
    periodo: str | None
    cantidad_observada: Real | None
    unidad: str | None


@dataclass(frozen=True)
class ResultadoErrorInsumo:
    lado: LadoRegistro
    insumo: str | None
    parcela_id: str | None
    periodo: str | None
    cantidad_requerida: float | None
    cantidad_observada: float | None
    unidad_requerida: str | None
    unidad_observada: str | None
    error_absoluto: float | None
    estado: EstadoComparacion
    motivo: str | None = None


@dataclass(frozen=True)
class ResultadoEvaluacionErrorInsumos:
    registros: tuple[ResultadoErrorInsumo, ...]
    n_evaluables: int
    n_no_evaluables_consumo_ausente: int
    n_no_comparables: int


def _semana_iso_valida(periodo: str | None) -> bool:
    if (
        not isinstance(periodo, str)
        or re.fullmatch(r"[0-9]{4}-W[0-9]{2}", periodo) is None
    ):
        return False
    try:
        date.fromisocalendar(int(periodo[:4]), int(periodo[6:]), 1)
    except ValueError:
        return False
    return True


def _clave_completa(insumo: str | None, parcela_id: str | None) -> bool:
    return (
        isinstance(insumo, str)
        and bool(insumo.strip())
        and isinstance(parcela_id, str)
        and bool(parcela_id.strip())
    )


def _claves_podrian_corresponder(
    izquierda: tuple[str | None, str | None, str | None],
    derecha: tuple[str | None, str | None, str | None],
) -> bool:
    for indice, (valor_izquierdo, valor_derecho) in enumerate(
        zip(izquierda, derecha)
    ):
        if indice == 2:
            informado_izquierdo = _semana_iso_valida(valor_izquierdo)
            informado_derecho = _semana_iso_valida(valor_derecho)
        else:
            informado_izquierdo = (
                isinstance(valor_izquierdo, str) and bool(valor_izquierdo.strip())
            )
            informado_derecho = (
                isinstance(valor_derecho, str) and bool(valor_derecho.strip())
            )
        if (
            informado_izquierdo
            and informado_derecho
            and valor_izquierdo != valor_derecho
        ):
            return False
    return True


def _cantidad_finita(valor: Real | None, nombre: str) -> float:
    if (
        valor is None
        or isinstance(valor, bool)
        or not isinstance(valor, Real)
    ):
        raise ValueError(f"{nombre} debe ser un número finito")
    try:
        valor_float = float(valor)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{nombre} debe ser un número finito") from exc
    if not isfinite(valor_float):
        raise ValueError(f"{nombre} debe ser un número finito")
    return valor_float


def _unidad_valida(unidad: str | None) -> bool:
    return isinstance(unidad, str) and bool(unidad.strip())


def evaluar_error_absoluto(
    estimaciones: list[EstimacionInsumo],
    consumos: list[ConsumoObservado],
) -> ResultadoEvaluacionErrorInsumos:
    """Compara estimaciones y consumos por insumo, parcela y semana ISO exactos.

    La igualdad exacta de unidad es el único criterio de compatibilidad: no se
    realizan conversiones. Un consumo sin registro coincidente se informa como
    ausente, salvo que exista un registro del mismo insumo/parcela en otro
    periodo, que se clasifica como no comparable.
    """
    if not isinstance(estimaciones, list) or not all(
        isinstance(registro, EstimacionInsumo) for registro in estimaciones
    ):
        raise TypeError("estimaciones debe ser una lista de EstimacionInsumo")
    if not isinstance(consumos, list) or not all(
        isinstance(registro, ConsumoObservado) for registro in consumos
    ):
        raise TypeError("consumos debe ser una lista de ConsumoObservado")

    cantidades_estimadas = [
        _cantidad_finita(registro.cantidad_requerida, "cantidad_requerida")
        for registro in estimaciones
    ]
    cantidades_observadas = [
        None
        if registro.cantidad_observada is None
        else _cantidad_finita(registro.cantidad_observada, "cantidad_observada")
        for registro in consumos
    ]

    claves_estimacion = [
        (registro.insumo, registro.parcela_id, registro.periodo)
        if _clave_completa(registro.insumo, registro.parcela_id)
        and _semana_iso_valida(registro.periodo)
        else None
        for registro in estimaciones
    ]
    claves_consumo = [
        (registro.insumo, registro.parcela_id, registro.periodo)
        if _clave_completa(registro.insumo, registro.parcela_id)
        and _semana_iso_valida(registro.periodo)
        else None
        for registro in consumos
    ]
    estimaciones_por_clave: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    consumos_por_clave: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for indice, clave in enumerate(claves_estimacion):
        if clave is not None:
            estimaciones_por_clave[clave].append(indice)
    for indice, clave in enumerate(claves_consumo):
        if clave is not None:
            consumos_por_clave[clave].append(indice)

    resultados: list[ResultadoErrorInsumo] = []
    estimaciones_reportadas: set[int] = set()
    consumos_reportados: set[int] = set()

    def agregar_estimacion(
        indice: int,
        estado: EstadoComparacion,
        motivo: str,
        *,
        indice_consumo: int | None = None,
        error: float | None = None,
    ) -> None:
        estimacion = estimaciones[indice]
        resultados.append(
            ResultadoErrorInsumo(
                lado="estimacion",
                insumo=estimacion.insumo,
                parcela_id=estimacion.parcela_id,
                periodo=estimacion.periodo,
                cantidad_requerida=cantidades_estimadas[indice],
                cantidad_observada=(
                    cantidades_observadas[indice_consumo]
                    if indice_consumo is not None
                    else None
                ),
                unidad_requerida=estimacion.unidad,
                unidad_observada=(
                    consumos[indice_consumo].unidad
                    if indice_consumo is not None
                    else None
                ),
                error_absoluto=error,
                estado=estado,
                motivo=motivo,
            )
        )
        estimaciones_reportadas.add(indice)

    def agregar_consumo(indice: int, motivo: str) -> None:
        consumo = consumos[indice]
        resultados.append(
            ResultadoErrorInsumo(
                lado="consumo",
                insumo=consumo.insumo,
                parcela_id=consumo.parcela_id,
                periodo=consumo.periodo,
                cantidad_requerida=None,
                cantidad_observada=cantidades_observadas[indice],
                unidad_requerida=None,
                unidad_observada=consumo.unidad,
                error_absoluto=None,
                estado="no_comparable",
                motivo=motivo,
            )
        )
        consumos_reportados.add(indice)

    for clave in dict.fromkeys(
        [*estimaciones_por_clave.keys(), *consumos_por_clave.keys()]
    ):
        indices_estimacion = estimaciones_por_clave.get(clave, [])
        indices_consumo = consumos_por_clave.get(clave, [])
        if len(indices_estimacion) > 1 or len(indices_consumo) > 1:
            for indice in indices_estimacion:
                agregar_estimacion(
                    indice, "no_comparable", "clave duplicada; emparejamiento ambiguo"
                )
            for indice in indices_consumo:
                agregar_consumo(indice, "clave duplicada; emparejamiento ambiguo")
            continue
        if not indices_estimacion or not indices_consumo:
            continue

        indice_estimacion = indices_estimacion[0]
        indice_consumo = indices_consumo[0]
        estimacion = estimaciones[indice_estimacion]
        consumo = consumos[indice_consumo]
        if not _unidad_valida(estimacion.unidad) or not _unidad_valida(consumo.unidad):
            agregar_estimacion(
                indice_estimacion,
                "no_comparable",
                "unidad ausente o inválida",
                indice_consumo=indice_consumo,
            )
        elif estimacion.unidad != consumo.unidad:
            agregar_estimacion(
                indice_estimacion,
                "no_comparable",
                "las unidades no son compatibles",
                indice_consumo=indice_consumo,
            )
        elif cantidades_observadas[indice_consumo] is None:
            agregar_estimacion(
                indice_estimacion,
                "consumo_ausente",
                "cantidad de consumo ausente",
                indice_consumo=indice_consumo,
            )
        else:
            cantidad_observada = cantidades_observadas[indice_consumo]
            assert cantidad_observada is not None
            agregar_estimacion(
                indice_estimacion,
                "evaluable",
                "claves y unidades compatibles",
                indice_consumo=indice_consumo,
                error=abs(
                    cantidades_estimadas[indice_estimacion] - cantidad_observada
                ),
            )
        consumos_reportados.add(indice_consumo)

    for indice, (estimacion, clave) in enumerate(zip(estimaciones, claves_estimacion)):
        if indice in estimaciones_reportadas:
            continue
        if clave is None:
            motivo = "claves incompletas o periodo ISO inválido en la estimación"
            estado: EstadoComparacion = "no_comparable"
        else:
            candidatos = []
            for candidato, consumo in enumerate(consumos):
                misma_identidad = (
                    _clave_completa(consumo.insumo, consumo.parcela_id)
                    and consumo.insumo == estimacion.insumo
                    and consumo.parcela_id == estimacion.parcela_id
                )
                identidad_incompleta_posible = (
                    not _clave_completa(consumo.insumo, consumo.parcela_id)
                    and _claves_podrian_corresponder(
                        clave,
                        (consumo.insumo, consumo.parcela_id, consumo.periodo),
                    )
                )
                if misma_identidad or identidad_incompleta_posible:
                    candidatos.append(candidato)
            if any(
                not _clave_completa(
                    consumos[candidato].insumo, consumos[candidato].parcela_id
                )
                or not _semana_iso_valida(consumos[candidato].periodo)
                for candidato in candidatos
            ):
                motivo = "hay consumo con claves incompletas o periodo inválido"
                estado = "no_comparable"
            elif candidatos:
                motivo = "hay consumo del mismo insumo y parcela en otro periodo"
                estado = "no_comparable"
            else:
                motivo = "no existe consumo observado para la clave"
                estado = "consumo_ausente"
        agregar_estimacion(indice, estado, motivo)

    for indice, (consumo, clave) in enumerate(zip(consumos, claves_consumo)):
        if indice in consumos_reportados:
            continue
        if clave is None:
            motivo = "claves incompletas o periodo ISO inválido en el consumo"
        else:
            estimaciones_potenciales = [
                estimacion
                for estimacion in estimaciones
                if _claves_podrian_corresponder(
                    clave,
                    (
                        estimacion.insumo,
                        estimacion.parcela_id,
                        estimacion.periodo,
                    ),
                )
            ]
            if any(
                not _clave_completa(estimacion.insumo, estimacion.parcela_id)
                or not _semana_iso_valida(estimacion.periodo)
                for estimacion in estimaciones_potenciales
            ):
                motivo = (
                    "posible relación con estimación de claves incompletas "
                    "o periodo inválido"
                )
            elif estimaciones_potenciales:
                motivo = "periodo sin coincidencia para la estimación"
            else:
                motivo = "no existe estimación correspondiente"
        agregar_consumo(indice, motivo)

    return ResultadoEvaluacionErrorInsumos(
        registros=tuple(resultados),
        n_evaluables=sum(registro.estado == "evaluable" for registro in resultados),
        n_no_evaluables_consumo_ausente=sum(
            registro.estado == "consumo_ausente" for registro in resultados
        ),
        n_no_comparables=sum(
            registro.estado == "no_comparable" for registro in resultados
        ),
    )
