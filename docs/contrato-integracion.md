# Contrato de integración — v1

> **Estado:** v1 — PROPUESTA. Los 5 puntos de la sección final se resolvieron con una decisión
> provisional para no bloquear T-02 y T-06 (ver DECISIONES.md D-007 a D-011). Cada una queda marcada
> como propuesta y debe confirmarse con los equipos 1 y 3 en sesión de seguimiento antes de la
> prueba de integración de la semana 12. Si algún equipo la objeta, se revisa y sube a v2.
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

Cada punto tiene ahora una **propuesta provisional** (ver DECISIONES.md). Siguen abiertos hasta
que los equipos 1 y 3 los confirmen o los objeten en sesión de seguimiento.

- [x] **Formato exacto del `parcela_id`** — propuesta: `P-NNN` (prefijo `P-`, tres dígitos,
  consecutivo asignado por el Equipo 1 en el aforamiento inicial de la parcela). Es el campo más
  peligroso: si un equipo lo genera distinto, la semana 12 se rompe. Ver D-007.
- [x] **Fuente de verdad del inventario** — propuesta: el Equipo 3 es la única fuente de verdad;
  nosotros solo leemos y nunca escribimos inventario, para no tener dos sistemas afirmando el
  mismo dato. Ver D-008.
- [x] **Frecuencia de actualización de las ventanas de despacho** — propuesta: el Equipo 3 las
  publica con mínimo 48 h de anticipación al inicio de la ventana; si cambian con menos margen,
  el plan ya generado no se recalcula automáticamente y queda como excepción trazada. Ver D-009.
- [x] **Autenticación entre servicios** — propuesta: token compartido por variable de entorno
  (`INTEGRACION_TOKEN`) en cabecera `Authorization: Bearer`, suficiente para el alcance académico;
  no se monta infraestructura de red privada. Ver D-010.
- [x] **Parcela sin aforar que el plan necesita** — propuesta: la parcela se excluye del plan de
  esa semana con `motivo: "sin_aforamiento"` en `item_plan`, no se estima a ciegas ni se bloquea
  el resto del plan. Ver D-011.
