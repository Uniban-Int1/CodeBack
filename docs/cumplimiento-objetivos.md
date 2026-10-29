# Cumplimiento de objetivos — Equipo 2

> Entregable del 29/10/2026. Relaciona los objetivos específicos del anteproyecto
> (`CONTEXT.md` §4) y los compromisos del correo del profesor (15/10) con la evidencia del
> repositorio y sus limitaciones. Todos los datos son **sintéticos** (D-006, D-019): no hubo
> acceso a registros históricos de Unibán.

Ejecutar todas las pruebas: `pytest` (203 pruebas).

## Objetivos específicos del anteproyecto

| Objetivo | Estado | Evidencia | Limitaciones |
|---|---|---|---|
| **1.** Modelar las variables de entrada y formalizarlas en un esquema y un contrato con los equipos 1 y 3 | ✅ | `app/models/entidades.py` y migración Alembic; `docs/modelo-datos.md`; `docs/contrato-integracion.md` v2; `docs/inventario-variables.md`; `config/parametros.yaml` | Unidades físicas de inventario y ventana real de embarque sin confirmar; la edad de racimo no está en ningún contrato |
| **2.** Proyección por parcela y periodo con modelo determinista y modelo predictivo, comparados contra una línea base ingenua | ⚠️ | Determinista: `app/core/proyeccion/base.py`. Predictivo: `predictivo.py` (regresión, folds temporales sin fuga). Comparación: `scripts/evaluar_modelos.py` y `GET /api/v1/modelos/evaluacion`. Pruebas: `test_caso_02`, `05`, `09`, `10`, `test_evaluacion_modelos.py` | **El predictivo no se entrenó con registros históricos** (no existen, D-019). Se evalúa en un escenario sintético con supuestos explícitos; no se adopta (D-003) |
| **3.** Módulo de programación (fecha de corte, secuencia, asignación de carga con capacidad y ventana) y derivación de insumos | ⚠️ | `app/core/programacion/` (fechas, restricciones, heurística); `app/core/insumos/estimacion.py`; `scripts/demo_programacion.py`. Pruebas: `test_caso_01`, `04`, `08`, `03`, `06`, `07` | La heurística multiparcela no está expuesta en la API: `/recomendar` evalúa una parcela con el vehículo por defecto. No reasigna cargas ni divide una parcela entre vehículos (D-002) |
| **4.** Evaluar con casos verificados a mano, error de predicción y dos escenarios de contraste | ✅ | Casos a mano en `tests/casos/` (docstrings con el cálculo); métricas en `docs/reporte-evaluacion.md`; escenario 2 (cambio de ventana) en `test_caso_12`; pruebas en vivo en `docs/pruebas-integracion.md` | Todo sintético; el error de estimación de insumos (D-015) no se pudo medir contra consumos reales |

## Compromisos del correo del profesor (Equipo 2)

| Compromiso | Estado | Dónde se ve |
|---|---|---|
| Modelo determinista funcional y validado para cajas, cartón y bolsas | ✅ | `/recomendar` en producción; `test_caso_02`, `03`, `06`, `07` |
| Modelo predictivo evaluado, con métricas y comparación frente al modelo base | ⚠️ | `scripts/evaluar_modelos.py`; pestaña Modelos de la app de demo. Con datos sintéticos, no históricos |
| Módulo de apoyo a la programación de cosecha y despacho | ✅ | `scripts/demo_programacion.py` (varios productores consolidados en vehículos) |
| Procesar aforamiento, cosecha esperada, inventarios, consumos y ventanas | ✅ | Todos entran en `/recomendar`. Los consumos se resumen por insumo y se comparan con lo requerido (`consumo_reciente`, `app/core/insumos/consumos.py`, `test_caso_13`) |
| Recomendaciones con cantidades requeridas, déficit o excedente y fechas | ✅ | Respuesta de `/recomendar` (`insumos[]`) |
| API funcional y documentada para el Equipo 3 | ✅ | `/docs` (Swagger) y `docs/contrato-integracion.md` v2 |
| Evidencia de pruebas, coherencia y trazabilidad | ✅ | 203 pruebas; `version_metodo` en cada respuesta (D-005); `docs/pruebas-integracion.md` |
| La recomendación se ve en el componente del Equipo 3 | ✅ | Capturas de la app Android del Equipo 3 (P3 en `docs/pruebas-integracion.md`) |
| Datos simulados identificados | ✅ | D-006, D-019; prefijo `sintetico_` y advertencias en cada salida |

## Guion de la demostración obligatoria

1. **Caso conocido:** desde la app del Equipo 3 (o el simulador), la parcela "La Esperanza" con
   1850 plantas y confianza 0.87 da 145.6 racimos, corte a las 12:55 y los insumos del cálculo a
   mano de `docs/pruebas-integracion.md`.
2. **Cambiar una variable:** inventario de cajas en 50 → aparece el déficit; cierre de ventana a
   las 08:00 → "ventana inalcanzable".
3. **Programación logística:** `python scripts/demo_programacion.py` y después
   `python scripts/demo_programacion.py 10:00` para ver cómo cambian el orden y la consolidación.
4. **Métricas del predictivo:** `python scripts/evaluar_modelos.py`. El predictivo le gana al
   determinista en todos los bloques, pero en el holdout la línea ingenua le gana a él, así que
   D-003 no se cumple y se mantiene `determinista-v1`.

## Limitaciones técnicas vigentes

1. **Sin datos históricos reales** (D-019): el predictivo y el error de insumos solo se evalúan
   con datos sintéticos.
2. **Consumos solo como referencia:** se resumen y se comparan con lo requerido, pero no
   recalibran los coeficientes ni miden el error de estimación de D-015, porque no hay forma de
   emparejar cada consumo con la cosecha que lo produjo.
3. **Heurística fuera del flujo integrado:** la consolidación de varios productores se demuestra
   aparte, no la pide el Equipo 3.
4. **Ventana de despacho sintética** y sin comparación con la hora actual en `/recomendar`.
5. **Fechas sin zona horaria:** se interpretan como hora local de Colombia; Render corre en UTC.
6. **Autenticación implementada pero apagada** (D-018).
7. **Base de datos free de Render:** expira el 20/11/2026.
8. **Reproducibilidad externa (T-21):** el README no se ha probado con una persona ajena al equipo.
