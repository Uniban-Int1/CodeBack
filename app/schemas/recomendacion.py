"""Esquemas Pydantic para el endpoint directo de recomendación de insumos y logística.

Soporta tanto el formato canónico del Equipo 2 como la estructura anidada enviada
por la app móvil del Equipo 3 (parcel, aforamiento, inventory, etc.), traduciendo esa
estructura a los campos canónicos.

Regla 4 del contrato (docs/contrato-integracion.md): si falta un dato de entrada
obligatorio, el sistema responde qué falta — no inventa el valor. Antes de esta
revisión, el validador rellenaba en silencio periodo, num_plantas_estimado,
calidad_confianza, inventario y ventana_despacho cuando faltaban; eso violaba la
regla 4 y producía recomendaciones basadas en datos ficticios sin avisar a nadie.
Ver DECISIONES.md D-017. El único default que se conserva es `tiempo_acarreo_min`
(cable vía estándar), que no estaba en el reclamo del Equipo 3 y no cambia el
resultado de forma tan crítica como los demás.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.ingesta import VentanaDespachoIngesta
from app.schemas.planes import (
    InsumoRequerimientoRespuesta,
    ItemPlanRespuesta,
    MetricasPlanRespuesta,
)


class SolicitudRecomendacion(BaseModel):
    """Payload de recomendación que acepta tanto formato directo como formato del Equipo 3."""
    model_config = ConfigDict(extra="ignore")  # Ignorar campos extras como losses, consumptions, etc.

    # Formato directo / canónico
    parcela_id: str | None = None
    periodo: str | None = None
    num_plantas_estimado: int | None = None
    calidad_confianza: float | None = None
    area_ha: float = 2.4
    tiempo_acarreo_min: int = 35
    ventana_despacho: VentanaDespachoIngesta | None = None
    inventario: dict[str, float] | None = None
    vehiculo_id: str | None = "V-3"
    capacidad_vehiculo_racimos: int = 420

    # Campos anidados provenientes del formato Equipo 3
    producerId: str | None = None
    parcel: dict[str, Any] | None = None
    aforamiento: dict[str, Any] | None = None
    inventory: list[dict[str, Any]] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalizar_payload_equipo3(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # 1. Traducir identificador de parcela y área desde parcel, si viene anidado
        parcel = data.get("parcel")
        if isinstance(parcel, dict):
            if not data.get("parcela_id"):
                identificador = parcel.get("id") or parcel.get("name")
                if identificador:
                    data["parcela_id"] = str(identificador)
            if "areaHa" in parcel and "area_ha" not in data:
                try:
                    data["area_ha"] = float(parcel["areaHa"])
                except (ValueError, TypeError):
                    pass

        # 2. Traducir aforamiento (estimatedPlants, confidence, period)
        aforamiento = data.get("aforamiento")
        if isinstance(aforamiento, dict):
            if "estimatedPlants" in aforamiento and data.get("num_plantas_estimado") is None:
                data["num_plantas_estimado"] = int(aforamiento["estimatedPlants"])
            if "confidence" in aforamiento and data.get("calidad_confianza") is None:
                data["calidad_confianza"] = float(aforamiento["confidence"])
            if "period" in aforamiento and not data.get("periodo"):
                data["periodo"] = str(aforamiento["period"])

        # 3. Traducir inventario desde la lista inventory[] del Equipo 3 (cajas, cartón, bolsas)
        inv_dict = data.get("inventario") if isinstance(data.get("inventario"), dict) else {}
        inventory_list = data.get("inventory")
        if isinstance(inventory_list, list):
            for item in inventory_list:
                if not isinstance(item, dict):
                    continue
                nombre_raw = str(item.get("name", "")).lower()
                cant = float(item.get("quantity", 0.0))
                if "caja" in nombre_raw:
                    inv_dict["cajas"] = cant
                elif "carton" in nombre_raw or "cartón" in nombre_raw:
                    inv_dict["carton"] = cant
                elif "bolsa" in nombre_raw:
                    inv_dict["bolsas"] = cant
        data["inventario"] = inv_dict

        # 4. Único default que se conserva: tiempo de acarreo estándar de cable vía.
        if data.get("tiempo_acarreo_min") is None:
            data["tiempo_acarreo_min"] = 35

        # Regla 4 del contrato: reportar lo que falta, no inventarlo.
        faltantes = []
        if not data.get("parcela_id"):
            faltantes.append("parcela_id (o parcel.id / parcel.name)")
        if not data.get("periodo"):
            faltantes.append("periodo (o aforamiento.period)")
        if data.get("num_plantas_estimado") is None:
            faltantes.append("num_plantas_estimado (o aforamiento.estimatedPlants)")
        if data.get("calidad_confianza") is None:
            faltantes.append("calidad_confianza (o aforamiento.confidence)")
        if not inv_dict:
            faltantes.append("inventario (o inventory[] con cajas/carton/bolsas)")
        if not data.get("ventana_despacho"):
            faltantes.append("ventana_despacho {inicio, fin}")

        if faltantes:
            raise ValueError(
                "Faltan datos obligatorios para generar la recomendación: "
                + "; ".join(faltantes)
            )

        return data


class RespuestaRecomendacion(BaseModel):
    """Respuesta directa entregada al Equipo 3."""
    parcela_id: str
    periodo: str
    volumen_racimos: float
    fecha_limite_corte: datetime
    cumple_ventana: bool
    version_metodo: str
    item_plan: ItemPlanRespuesta
    insumos: list[InsumoRequerimientoRespuesta]
    metricas: MetricasPlanRespuesta
