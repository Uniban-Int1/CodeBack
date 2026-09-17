# Contrato de integración — v1

> **Estado:** BORRADOR. Debe acordarse con los equipos 1 y 3 antes de cerrar la semana 6 (T-01).
> **Responsable de publicar y versionar:** Equipo 2.
> Los cambios se acuerdan en sesión de seguimiento y se numeran v1, v2…

Somos seis subproyectos, no seis islas. Este documento es la frontera entre los tres equipos
del proyecto Plátano–Unibán.

---

## Recibimos del Equipo 1 — Aforamiento

`POST /api/v1/ingesta/aforamiento`

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `parcela_id` | string | sí | identificador acordado entre los tres equipos |
| `fecha` | date | sí | fecha del aforamiento |
| `area_ha` | float | sí | superficie de la parcela |
| `num_plantas_estimado` | int | sí | resultado del conteo |
| `calidad_confianza` | float 0–1 | sí | **no opcional**: la recomendación viaja con esta confianza |

```json
{
  "parcela_id": "P-018",
  "fecha": "2026-09-14",
  "area_ha": 2.4,
  "num_plantas_estimado": 1850,
  "calidad_confianza": 0.87
}
```

Alternativa aceptada: archivo CSV versionado con las mismas columnas.

---

## Recibimos del Equipo 3 — Gestión operativa

`POST /api/v1/ingesta/operacion`

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `parcela_id` | string | sí | |
| `acopio_id` | string | sí | a qué acopio va esa parcela |
| `tiempo_acarreo_min` | int | sí | de la parcela al acopio |
| `medio_acarreo` | enum | sí | `cable_via` \| `traccion_animal` \| `otro` |
| `capacidad_medio_racimos` | int | sí | racimos por viaje del medio |
| `vehiculos[]` | array | sí | disponibles en el periodo, con capacidad |
| `ventana_despacho` | object | sí | inicio y fin |
| `inventario[]` | array | sí | por insumo y parcela |
| `consumos[]` | array | no | histórico de consumo real, para validar |

```json
{
  "parcela_id": "P-018",
  "acopio_id": "AC-02",
  "tiempo_acarreo_min": 35,
  "medio_acarreo": "cable_via",
  "capacidad_medio_racimos": 65,
  "vehiculos": [{"id": "V-3", "capacidad_racimos": 420}],
  "ventana_despacho": {"inicio": "2026-09-21T06:00", "fin": "2026-09-21T16:00"},
  "inventario": [{"insumo": "cajas", "cantidad": 300}],
  "consumos": [{"insumo": "cajas", "periodo": "2026-W37", "cantidad": 412}]
}
```

---

## Entregamos al Equipo 3 — Plan y requerimiento de insumos

`GET /api/v1/planes/{periodo}`

```json
{
  "plan_id": "PL-2026-W38",
  "periodo": "2026-W38",
  "version_metodo": "heuristica-v1",
  "generado_en": "2026-09-17T09:12:00",
  "items": [
    {
      "parcela_id": "P-018",
      "fecha_corte": "2026-09-20",
      "vehiculo_id": "V-3",
      "orden": 2,
      "carga_estimada_racimos": 210,
      "cumple_ventana": true,
      "motivo": null
    }
  ],
  "insumos": [
    {
      "insumo": "cajas",
      "fecha": "2026-09-20",
      "cantidad_requerida": 412,
      "inventario_disponible": 300,
      "deficit": 112
    }
  ],
  "metricas": {
    "cumplimiento_ventana": 0.92,
    "uso_capacidad": 0.78
  }
}
```

---

## Reglas

1. **Formato:** JSON por API REST. El Equipo 1 puede alternativamente entregar CSV versionado.
2. **Versionado:** `v1`, `v2`… Un cambio que rompa compatibilidad sube la versión mayor.
3. **`version_metodo` es obligatorio** en toda salida: sin él la recomendación no es trazable (D-005).
4. **Degradación controlada:** si falta un dato de entrada, el sistema responde qué falta,
   no se cae ni inventa el valor.
5. **Prueba de integración conjunta: semana 12**, con datos reales de los tres equipos.

---

## Pendientes por acordar (T-01)

- [ ] Formato exacto del `parcela_id` — que sea el mismo en los tres equipos
- [ ] Quién es la fuente de verdad del inventario: ¿Equipo 3 siempre?
- [ ] Frecuencia de actualización de las ventanas de despacho
- [ ] Autenticación entre servicios: ¿token compartido o red interna?
- [ ] Qué pasa si el Equipo 1 no ha aforado una parcela que el plan necesita
