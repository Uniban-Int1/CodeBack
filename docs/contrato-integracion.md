# Contrato de integración — v2 (referencia técnica)

> **Contrato acordado Equipo 3 ↔ Equipo 2:** el documento del Equipo 3,
> [`docs/contrato-equipo2.md`](https://github.com/JuanSebastian05/uniban-app-suministros/blob/main/docs/contrato-equipo2.md)
> en su repositorio, adoptado por ambos equipos el 28/10/2026. Es la versión que se presenta
> como contrato de la integración.
>
> **Este documento** es la referencia técnica del servicio del Equipo 2: detalla campos,
> unidades, valores por defecto y errores de `POST /api/v1/recomendar`, y debe coincidir con
> el contrato acordado. Si difieren, se corrige el que esté desactualizado en la siguiente
> sesión de seguimiento. Integración verificada el 28/10/2026 contra los dos backends
> desplegados (ver `docs/pruebas-integracion.md`).
> **Responsable de este documento:** Equipo 2. Las horas se expresan en hora local de
> Colombia, sin zona horaria explícita.

Somos seis subproyectos, no seis islas. Este documento es la frontera entre los tres equipos
del proyecto Plátano–Unibán. La arquitectura completa está en `docs/arquitectura.md`.

## Cambios de v1 a v2

| Cambio | Por qué | Rompe compatibilidad |
|---|---|---|
| Nueva interfaz principal `POST /api/v1/recomendar` (sección siguiente) | Es la que usa el Equipo 3 en producción; v1 no la documentaba | — |
| `ventana_despacho`, `periodo`, `num_plantas_estimado`, `calidad_confianza` e inventario pasan a ser obligatorios en `/recomendar` | Regla 4: antes se inventaban valores por defecto (D-017) | **Sí** |
| `parcela_id` es el UUID del sistema de origen, no `P-NNN` | D-016 | No (ya era texto libre) |
| La respuesta incluye `excedente` por insumo | D-013, pedido en `contrato-equipo2.md` del Equipo 3 | No (campo nuevo) |
| `consumptions[]` se procesa y vuelve resumido en `consumo_reciente` | Antes se recibía y se descartaba | No (campo nuevo) |
| `POST /ingesta/*` y `GET /planes/{periodo}` quedan definidos pero **sin uso** | En la práctica, el aforamiento llega por el Equipo 3 y el plan se pide por parcela | — |

---

## Interfaz en uso: el Equipo 3 pide la recomendación — `POST /api/v1/recomendar`

URL de producción: `https://platano-logistica-api.onrender.com/api/v1/recomendar`
Documentación interactiva: `https://platano-logistica-api.onrender.com/docs`

**Quién llama:** el backend del Equipo 3 (`uniban-app-suministros.onrender.com`), cuando el
productor pide una recomendación en la app. La app nunca nos llama directamente.
**Autenticación:** ninguna por ahora. Está implementada (`Authorization: Bearer <token>`, D-018),
pero apagada hasta coordinar la activación. **No** es una cabecera `X-API-Key`.
**Despertar el servicio:** el plan free de Render duerme el servicio; conviene llamar antes a
`GET /salud` y usar al menos 90 s de espera (el cliente del Equipo 3 ya lo hace).

### Solicitud

Acepta el formato anidado del Equipo 3 y el formato directo, o ambos a la vez (el directo tiene
prioridad). Campos usados:

| Dato | Formato anidado (Equipo 3) | Formato directo | Tipo y unidad | Obligatorio |
|---|---|---|---|---|
| Parcela | `parcel.id` | `parcela_id` | texto, UUID del sistema de origen | sí |
| Periodo | `aforamiento.period` | `periodo` | semana ISO, `2026-W44` | sí |
| Plantas aforadas | `aforamiento.estimatedPlants` | `num_plantas_estimado` | entero, plantas | sí |
| Confianza del aforamiento | `aforamiento.confidence` | `calidad_confianza` | decimal 0–1 | sí (`null` = faltante) |
| Inventario de empaque | `inventory[]` (`name`, `quantity`) | `inventario` (`{"cajas": n, ...}`) | unidades; nombres `cajas`, `carton`, `bolsas` | sí |
| Ventana de despacho | — | `ventana_despacho.inicio` / `.fin` | fecha y hora local, sin zona (`2026-10-30T06:00:00`) | sí |
| Tiempo de acarreo | — | `tiempo_acarreo_min` | minutos | no (35 por defecto, cable vía) |
| Vehículo | — | `vehiculo_id`, `capacidad_vehiculo_racimos` | texto; racimos | no (`V-3`, 420) |
| Área | `parcel.areaHa` | `area_ha` | hectáreas | no (informativa, no entra en el cálculo) |

`consumptions[]` (opcional: `name`, `quantity`, `date`) se resume por insumo de empaque y
vuelve en `consumo_reciente` (ver la respuesta). Los registros que no son de empaque o no
traen una cantidad válida se ignoran.

Se aceptan y **se ignoran**: `producerId`, `parcel.name`, `parcel.activeCycle`,
`aforamiento.date` e `inventory[].supplyId/category/unit`. En el inventario, si llegan varios
ítems con el mismo nombre, se conserva el último: el Equipo 3 ya los envía sumados.

Ejemplo real (el que arma el backend del Equipo 3):

```json
{
  "producerId": "33333333-3333-4333-8333-333333333333",
  "parcel": {"id": "11111111-1111-4111-8111-111111111111", "name": "La Esperanza", "areaHa": 2.4},
  "aforamiento": {"date": "2026-10-29", "period": "2026-W44", "estimatedPlants": 1850, "confidence": 0.87},
  "inventory": [
    {"name": "cajas", "category": "Empaque", "unit": "unidad", "quantity": 80},
    {"name": "carton", "category": "Empaque", "unit": "unidad", "quantity": 120},
    {"name": "bolsas", "category": "Empaque", "unit": "unidad", "quantity": 200}
  ],
  "ventana_despacho": {"inicio": "2026-10-30T06:00:00", "fin": "2026-10-30T16:00:00"},
  "consumptions": [],
  "parcela_id": "11111111-1111-4111-8111-111111111111",
  "periodo": "2026-W44",
  "num_plantas_estimado": 1850,
  "area_ha": 2.4,
  "calidad_confianza": 0.87
}
```

**Sobre la ventana:** nadie tiene hoy la ventana real de embarque, así que el Equipo 3 envía
una sintética. Debe estar **en el futuro respecto al momento de la consulta** (por ejemplo,
mañana de 06:00 a 16:00). Si se calcula desde la fecha del aforamiento, puede caer en el
pasado, y `/recomendar` todavía no compara contra la hora actual.

### Respuesta (200)

```json
{
  "parcela_id": "11111111-1111-4111-8111-111111111111",
  "periodo": "2026-W44",
  "volumen_racimos": 145.6,
  "fecha_limite_corte": "2026-10-30T12:55:00",
  "cumple_ventana": true,
  "version_metodo": "determinista-v1",
  "item_plan": {
    "parcela_id": "11111111-1111-4111-8111-111111111111",
    "fecha_corte": "2026-10-30T12:55:00",
    "vehiculo_id": "V-3",
    "orden": 1,
    "carga_estimada_racimos": 146,
    "cumple_ventana": true,
    "motivo": null
  },
  "insumos": [
    {"insumo": "cajas", "fecha": "2026-10-30", "cantidad_requerida": 123.76, "inventario_disponible": 80.0, "deficit": 43.76, "excedente": 0.0},
    {"insumo": "carton", "fecha": "2026-10-30", "cantidad_requerida": 123.76, "inventario_disponible": 120.0, "deficit": 3.76, "excedente": 0.0},
    {"insumo": "bolsas", "fecha": "2026-10-30", "cantidad_requerida": 145.6, "inventario_disponible": 200.0, "deficit": 0.0, "excedente": 54.4}
  ],
  "metricas": {"cumplimiento_ventana": 1.0, "uso_capacidad": 0.35}
}
```

| Campo | Significado | Unidad |
|---|---|---|
| `volumen_racimos` | Cosecha proyectada de la parcela en el periodo | racimos |
| `fecha_limite_corte` | Hora más tardía de corte que aún alcanza la ventana (fin − empaque − acarreo − margen) | fecha y hora local |
| `cumple_ventana` | El corte, el acarreo y el empaque caben antes del cierre de la ventana | — |
| `item_plan.carga_estimada_racimos` | Volumen proyectado redondeado | racimos |
| `insumos[].cantidad_requerida` | volumen × coeficiente de consumo (`config/parametros.yaml`) | unidades |
| `insumos[].deficit` / `excedente` | Diferencia positiva entre lo requerido y el inventario, en un sentido u otro | unidades |
| `insumos[].fecha` | Fecha para la que se necesita el insumo (la del corte) | fecha |
| `metricas.uso_capacidad` | carga / capacidad del vehículo | proporción 0–1 |
| `version_metodo` | Método que produjo el resultado (D-005) | — |
| `consumo_reciente[]` | Por insumo con consumos recibidos: `registros`, `total`, `promedio_por_registro`, `ultima_fecha`, `ultima_cantidad`, `requerido` y `diferencia_requerido_vs_promedio` (positivo = esta cosecha pide más que lo habitual). Vacío si no se enviaron consumos | unidades |

`cumple_ventana` mide solo el tiempo. Un déficit de insumos no lo vuelve falso: se interpreta
como "comprar antes de la hora de corte".

### Errores

| Código | Cuándo | Qué hacer |
|---|---|---|
| 422 | Falta un dato obligatorio o es `null`. El mensaje lista **todos** los que faltan | Corregir la solicitud; reintentar no sirve |
| 422 | `ventana_despacho.fin` ≤ `inicio` | Corregir la ventana |
| 5xx o sin respuesta | Servicio dormido o caído | Reintentar después de `GET /salud` |

Si la ventana no alcanza (acarreo más empaque no caben), la respuesta es **200** con
`cumple_ventana: false` y `motivo: "ventana_despacho_inalcanzable_por_acarreo_o_empaque"`.

---

## Otros servicios publicados

- `GET /salud` — estado del servicio.
- `GET /api/v1/modelos/evaluacion` — compara predictivo, determinista e ingenuo sobre un
  escenario sintético declarado (T-14, D-003). Solo lectura.
- `GET /api/v1/parametros` — parámetros del dominio vigentes (`config/parametros.yaml`).

---

## Definido en v1, sin uso en el flujo integrado

Las secciones siguientes se mantienen como referencia. En la práctica el Equipo 1 entrega el
aforamiento al Equipo 3 (`docs/integracion-equipo1.txt` en su repositorio) y el Equipo 3 nos lo
reenvía dentro de `/recomendar`.

---

## Recibimos del Equipo 1 — Aforamiento

`POST /api/v1/ingesta/aforamiento`

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `parcela_id` | string (UUID) | sí | identificador que ya genera el sistema de origen — ver D-016 |
| `fecha` | date | sí | fecha del aforamiento |
| `area_ha` | float | sí | superficie de la parcela |
| `num_plantas_estimado` | int | sí | resultado del conteo |
| `calidad_confianza` | float 0–1 | sí | **no opcional**: la recomendación viaja con esta confianza |

```json
{
  "parcela_id": "11111111-1111-4111-8111-111111111111",
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
| `inventario[]` | array | sí | por insumo y parcela. Unidad física, periodo/fecha de corte, frecuencia de actualización y diferencia entre saldo cero y dato ausente pendientes de confirmar con el Equipo 3; ver D-008 y `docs/inventario-variables.md`. |
| `consumos[]` | array | no | histórico de consumo real, para validar |

```json
{
  "parcela_id": "11111111-1111-4111-8111-111111111111",
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

El ejemplo de `inventario[]` solo ilustra la forma provisional del dato: `cantidad` no
define una unidad física ni expresa por sí misma el periodo o la actualidad del saldo.
Esos elementos siguen pendientes de confirmación con el Equipo 3; el ejemplo no constituye
evidencia de un extracto real de Unibán.

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
      "parcela_id": "11111111-1111-4111-8111-111111111111",
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
6. **Parcela esperada sin aforamiento:** se excluye de proyección y programación y se informa
   fuera de `item_plan`, con `parcela_id` y `motivo: "sin_aforamiento"`. No se generan fecha de
   corte ni carga estimada ficticias.

---

## Pendientes por acordar (T-01)

Cada punto tiene ahora una **propuesta provisional** (ver DECISIONES.md). Siguen abiertos hasta
que los equipos 1 y 3 los confirmen o los objeten en sesión de seguimiento.

- [x] **Formato exacto del `parcela_id`** — CERRADO (D-016): se adopta el identificador que ya
  genera el sistema de origen (Equipo 1 o Equipo 3), en la práctica un UUID. Ya no se exige
  `P-NNN` (D-007, superada). Lo que sigue abierto no es el formato, sino confirmar que el
  Equipo 1 y el Equipo 3 usan el mismo valor para la misma parcela — ese es el riesgo real para
  la semana 12.
- [x] **Fuente de verdad del inventario** — propuesta: el Equipo 3 es la única fuente de verdad;
  nosotros solo leemos y nunca escribimos inventario, para no tener dos sistemas afirmando el
  mismo dato. Ver D-008.
- [x] **Frecuencia de actualización de las ventanas de despacho** — propuesta: el Equipo 3 las
  publica con mínimo 48 h de anticipación al inicio de la ventana; si cambian con menos margen,
  el plan ya generado no se recalcula automáticamente y queda como excepción trazada. Ver D-009.
- [x] **Autenticación entre servicios** — propuesta: token compartido por variable de entorno
  (`INTEGRACION_TOKEN`) en cabecera `Authorization: Bearer`, suficiente para el alcance académico;
  no se monta infraestructura de red privada. Ver D-010.
- [x] **Parcela sin aforar que el plan necesita** — propuesta: se excluye de proyección y
  programación y se reporta aparte de `item_plan` con `parcela_id` y
  `motivo: "sin_aforamiento"`; no se estima a ciegas ni se bloquea el resto del plan. Ver D-011.
