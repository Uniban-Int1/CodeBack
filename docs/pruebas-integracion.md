# Pruebas de integración Equipo 3 ↔ Equipo 2

> Ejecutadas el 28/10/2026 contra los servicios desplegados en Render. Datos de prueba
> controlados y **sintéticos** (D-006, D-019). Cada prueba se puede reproducir con el comando
> indicado.

URL del Equipo 2: `https://platano-logistica-api.onrender.com`
URL del Equipo 3: `https://uniban-app-suministros.onrender.com`

## Resumen

| # | Prueba | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| P1 | Ambos servicios responden | 200 | ✅ E2 `/salud` 200 (~30 s en despertar) · E3 `/health` 200 |
| P2 | Solicitud completa con el formato del Equipo 3 | 200 con recomendación | ✅ 200; valores verificados a mano (abajo) |
| P3 | Recomendación recibida y visible en la app del Equipo 3 | Mismos valores que P2 | ✅ Capturas del Equipo 3: 145.6 racimos, corte 12:55, déficits 96.67 / 76.67 / 141.2 |
| P4 | Solicitud sin `ventana_despacho` | 422 que nombra el campo | ✅ 422 `Faltan datos obligatorios...: ventana_despacho {inicio, fin}` |
| P5 | Aforamiento con `confidence: null` | 422 que nombra el campo | ❌ → ✅ Devolvía 500; corregido en `52b2283`, ahora 422 |
| P6 | Consultas que leen la base (`/planes`, `/insumos`) | 404 si no hay plan | ❌ → ✅ Devolvían 500 (tablas sin crear); corregido en `4b9dec4`, ahora 404 |
| P7 | Ventana ya pasada | `cumple_ventana: false` | ⚠️ Responde `true`. Limitación conocida, ver abajo |
| P8 | Simulador de la app del Equipo 2 contra Render | "Fuente: backend en vivo" | ✅ iPhone vía Expo Go, mismos valores que P2 |
| P9 | Sin cabecera de autenticación | Pasa (token apagado, D-018) | ✅ Pasa; con token activo se cubre en `tests/test_seguridad_integracion.py` |

## Detalle

### P2 — Solicitud completa (cálculo a mano)

```bash
curl -X POST https://platano-logistica-api.onrender.com/api/v1/recomendar \
  -H "Content-Type: application/json" \
  -d '{"parcel":{"id":"11111111-1111-4111-8111-111111111111","areaHa":2.4},
       "aforamiento":{"period":"2026-W44","estimatedPlants":1850,"confidence":0.87},
       "inventory":[{"name":"cajas","quantity":27.09},{"name":"carton","quantity":47.09},{"name":"bolsas","quantity":4.4}],
       "ventana_despacho":{"inicio":"2026-10-28T06:00:00","fin":"2026-10-28T16:00:00"}}'
```

| Resultado | Cálculo | Valor |
|---|---|---|
| Volumen | 1850 × (1/10.5) × 0.87 × (1 − 0.05) | 145.6 racimos |
| Hora límite | 16:00 − (120 empaque + 35 acarreo + 30 margen) | 12:55 |
| Cajas | 145.6 × 0.85 = 123.76; déficit 123.76 − 27.09 | 96.67 |
| Cartón | 145.6 × 0.85 = 123.76; déficit 123.76 − 47.09 | 76.67 |
| Bolsas | 145.6 × 1.00 = 145.6; déficit 145.6 − 4.4 | 141.2 |
| Uso de capacidad | 145.6 / 420 | 0.35 |

Son exactamente los valores que muestra la app del Equipo 3 (P3), así que la información
llega sin conversiones manuales.

### P5 — `confidence: null`

El contrato Equipo 1 → Equipo 3 permite omitir la confianza o enviarla `null`. El normalizador
hacía `float(None)` y respondía 500; el cliente del Equipo 3 lo interpretaba como "servicio no
disponible" y reintentaba. Ahora un `null` cuenta como dato faltante y se responde 422
(`tests/test_api_recomendacion.py::test_recomendar_confianza_null_responde_422_no_500`).

### P6 — Tablas sin crear en producción

Los registros de Render mostraban `relation "plan_recoleccion" does not exist`: las migraciones
nunca se habían aplicado. El "Pre-Deploy Command" está bloqueado en el plan free, así que la
migración se movió al arranque del contenedor (`Dockerfile`: `alembic upgrade head && uvicorn ...`).
El registro del despliegue confirma `Running upgrade -> 1c9c07620028, esquema inicial`.

### P7 — Ventana ya pasada (abierta)

La recomendación que muestra la app del Equipo 3 se generó el 28/10 a las 18:48, con hora
límite 12:55 del mismo día, y aun así dice que cumple. El Equipo 3 arma la ventana como
"fecha del aforamiento + 1 día", y `/recomendar` no compara contra la hora actual. La
heurística multiparcela sí lo hace (`"la fecha límite de corte ya venció"`).
Acción: el Equipo 3 calculará la ventana desde **hoy + 1**.

## Pendiente de verificar en conjunto

- Cadena completa con el Equipo 1: imagen → inferencia → `POST /api/v1/aforamientos` (E3) →
  recomendación (E2) → app (E3). El tramo E1 → E3 no lo ha verificado el Equipo 2.
- Activación del token (D-018) con el cliente del Equipo 3, que hoy envía `X-API-Key`.
