"""Esquemas Pydantic para el endpoint directo de recomendación de insumos y logística.

Soporta tanto el formato canónico del Equipo 2 como la estructura anidada enviada
por la app móvil del Equipo 3 (parcel, aforamiento, inventory, etc.),
asignando valores por defecto a tiempos de acarreo y ventanas de despacho
si el Equipo 3 no los envía.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
from datetime import date, datetime, time
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
    calidad_confianza: float = 0.87
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

        # 1. Extraer identificador de parcela y área desde parcel (si viene anidado)
        parcel = data.get("parcel")
        if isinstance(parcel, dict):
            if not data.get("parcela_id"):
                data["parcela_id"] = str(parcel.get("id") or parcel.get("name") or "P-001")
            if "areaHa" in parcel and "area_ha" not in data:
                try:
                    data["area_ha"] = float(parcel["areaHa"])
                except (ValueError, TypeError):
                    pass

        # 2. Extraer aforamiento (estimatedPlants, confidence, date, period)
        aforamiento = data.get("aforamiento")
        aforamiento_fecha = None
        if isinstance(aforamiento, dict):
            if "estimatedPlants" in aforamiento and not data.get("num_plantas_estimado"):
                data["num_plantas_estimado"] = int(aforamiento["estimatedPlants"])
            if "confidence" in aforamiento and "calidad_confianza" not in data:
                data["calidad_confianza"] = float(aforamiento["confidence"])
            if "period" in aforamiento and not data.get("periodo"):
                data["periodo"] = str(aforamiento["period"])
            if "date" in aforamiento:
                try:
                    aforamiento_fecha = date.fromisoformat(str(aforamiento["date"]))
                except ValueError:
                    aforamiento_fecha = None

        # Si aún no hay periodo, usar valor por defecto
        if not data.get("periodo"):
            data["periodo"] = "2026-W38"

        # Si aún no hay num_plantas_estimado, usar un valor por defecto seguro (ej. 1850)
        if data.get("num_plantas_estimado") is None:
            data["num_plantas_estimado"] = 1850

        # Si no hay parcela_id, asignar valor por defecto
        if not data.get("parcela_id"):
            data["parcela_id"] = "P-018"

        # 3. Extraer y mapear inventario desde la lista del Equipo 3 (cajas, cartón, bolsas)
        inv_dict = data.get("inventario")
        if not isinstance(inv_dict, dict):
            inv_dict = {"cajas": 300.0, "carton": 400.0, "bolsas": 350.0}

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

        # 4. Asignar ventana de despacho por defecto si el Equipo 3 no la envía
        # Regla por defecto: el mismo día de la fecha de aforamiento/corte, de 06:00 a 16:00 hrs
        if not data.get("ventana_despacho"):
            fecha_ref = aforamiento_fecha or date(2026, 9, 21)
            inicio_dt = datetime.combine(fecha_ref, time(6, 0))
            fin_dt = datetime.combine(fecha_ref, time(16, 0))
            data["ventana_despacho"] = {
                "inicio": inicio_dt,
                "fin": fin_dt,
            }

        # 5. Tiempo de acarreo por defecto (35 minutos cable vía estándar)
        if "tiempo_acarreo_min" not in data or data.get("tiempo_acarreo_min") is None:
            data["tiempo_acarreo_min"] = 35

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
