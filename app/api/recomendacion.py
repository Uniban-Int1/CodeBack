"""Router de recomendación de insumos y logística de cosecha.

Permite al Equipo 3 enviar los datos de aforamiento, inventario y ventana
de despacho de una parcela, y recibir de inmediato la recomendación
calculada por el motor determinista y la heurística de corte.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from app.core.programacion.fechas import VentanaDespacho, VentanaInalcanzable
from app.core.proyeccion.base import Aforamiento
from app.core.servicio import recomendar_insumos
from app.schemas.planes import (
    InsumoRequerimientoRespuesta,
    ItemPlanRespuesta,
    MetricasPlanRespuesta,
)
from app.schemas.recomendacion import (
    RespuestaRecomendacion,
    SolicitudRecomendacion,
)

router = APIRouter()


@router.post(
    "/recomendar",
    response_model=RespuestaRecomendacion,
    status_code=status.HTTP_200_OK,
    summary="Generar recomendación inmediata (Equipo 3)",
    description=(
        "Recibe parcela, aforamiento, inventario y ventana de despacho, "
        "y retorna de inmediato el plan de corte y requerimiento de insumos."
    ),
)
def generar_recomendacion(
    solicitud: SolicitudRecomendacion,
) -> RespuestaRecomendacion:
    """Ejecuta el motor determinista y de corte en vivo para la solicitud recibida."""
    if solicitud.ventana_despacho.fin <= solicitud.ventana_despacho.inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha/hora de fin de la ventana de despacho debe ser posterior a la de inicio.",
        )

    ventana = VentanaDespacho(
        inicio=solicitud.ventana_despacho.inicio,
        fin=solicitud.ventana_despacho.fin,
    )

    aforamiento = Aforamiento(
        parcela_id=solicitud.parcela_id,
        num_plantas=solicitud.num_plantas_estimado,
        area_ha=solicitud.area_ha,
        calidad_confianza=solicitud.calidad_confianza,
    )

    cumple_ventana = True
    motivo = None

    try:
        rec = recomendar_insumos(
            aforamiento=aforamiento,
            ventana=ventana,
            inventario=solicitud.inventario,
            periodo=solicitud.periodo,
            minutos_acarreo=solicitud.tiempo_acarreo_min,
        )
        fecha_corte = rec.fecha_limite_corte
    except VentanaInalcanzable:
        cumple_ventana = False
        motivo = "ventana_despacho_inalcanzable_por_acarreo_o_empaque"
        fecha_corte = solicitud.ventana_despacho.fin
        # En caso de ventana inalcanzable, igual derivamos los insumos
        from app.config import parametros
        from app.core.insumos.estimacion import estimar
        from app.core.proyeccion.base import proyectar

        params = parametros()
        proy = proyectar(
            aforamiento,
            periodo=solicitud.periodo,
            ciclo_racimo_semanas=params["proyeccion"]["ciclo_racimo_semanas"],
            factor_perdida=params["proyeccion"]["factor_perdida"],
        )
        reqs = estimar(
            volumen_racimos=proy.volumen_racimos,
            fecha=fecha_corte.date(),
            coeficientes=params["consumo_unitario"],
            inventario=solicitud.inventario,
        )
        from app.core.servicio import RecomendacionInsumos
        rec = RecomendacionInsumos(
            parcela_id=proy.parcela_id,
            periodo=proy.periodo,
            volumen_racimos=proy.volumen_racimos,
            fecha_limite_corte=fecha_corte,
            requerimientos=reqs,
            version_metodo=proy.metodo,
        )

    # Convertir requerimientos a esquema Pydantic
    insumos_resp = [
        InsumoRequerimientoRespuesta(
            insumo=r.insumo,
            fecha=r.fecha,
            cantidad_requerida=r.cantidad_requerida,
            inventario_disponible=r.inventario_disponible,
            deficit=r.deficit,
            excedente=r.excedente,
        )
        for r in rec.requerimientos
    ]

    item_plan = ItemPlanRespuesta(
        parcela_id=solicitud.parcela_id,
        fecha_corte=fecha_corte,
        vehiculo_id=solicitud.vehiculo_id,
        orden=1,
        carga_estimada_racimos=int(round(rec.volumen_racimos)),
        cumple_ventana=cumple_ventana,
        motivo=motivo,
    )

    capacidad_total = solicitud.capacidad_vehiculo_racimos
    uso_capacidad = round(min(1.0, rec.volumen_racimos / capacidad_total), 2) if capacidad_total > 0 else 0.0

    return RespuestaRecomendacion(
        parcela_id=solicitud.parcela_id,
        periodo=solicitud.periodo,
        volumen_racimos=rec.volumen_racimos,
        fecha_limite_corte=fecha_corte,
        cumple_ventana=cumple_ventana,
        version_metodo=rec.version_metodo,
        item_plan=item_plan,
        insumos=insumos_resp,
        metricas=MetricasPlanRespuesta(
            cumplimiento_ventana=1.0 if cumple_ventana else 0.0,
            uso_capacidad=uso_capacidad,
        ),
    )
