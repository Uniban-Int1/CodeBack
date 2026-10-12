# Inventario de variables — disponibilidad y huecos

> Evidencia de T-04. Insumo para decidir si el modelo predictivo (T-14) es viable y
> para que T-05 sepa qué parámetros puede levantar con dato real y cuáles quedan
> `PENDIENTE` en `config/parametros.yaml`.
> Responsable: Camilo — frente backend.
> **Estado de T-04: pendiente de verificación con datos reales.** El repositorio no
> contiene un extracto del histórico de Unibán que permita confirmar disponibilidad,
> tipos, unidades o cobertura temporal reales. La información de contrato que sigue
> es lo propuesto o acordado provisionalmente con los equipos, no evidencia de una
> entrega real.

| Variable | Fuente responsable | Tipo indicado en contrato/documentación | Unidad | Estado según contrato | Verificación en datos reales | Cobertura temporal |
|---|---|---|---|---|---|---|
| `parcela_id` | Equipo 1 / Equipo 3 | string | No aplica | Presente como requerido en el contrato; formato `P-NNN` es propuesta D-007 | Pendiente | No aplica; disponibilidad del identificador real pendiente |
| `fecha` de aforamiento | Equipo 1 | date | Fecha calendario | Presente como requerido en el contrato | Pendiente | Por aforamiento según contrato; serie histórica y rango de fechas pendientes |
| `area_ha` | Equipo 1 | float | hectáreas (`ha`) | Presente como requerido en el contrato | Pendiente | Por aforamiento según contrato; rango histórico pendiente |
| `num_plantas_estimado` | Equipo 1 | int | plantas | Presente como requerido en el contrato | Pendiente | Por aforamiento según contrato; frecuencia y rango histórico pendientes |
| `calidad_confianza` | Equipo 1 | float, rango contractual 0–1 | Adimensional | Presente como requerido en el contrato | Pendiente | Por aforamiento según contrato; frecuencia y rango histórico pendientes |
| `edad_racimo` (semanas) o fecha de floración | Equipo 1; fuente no definida en el contrato actual | No definido en el contrato | Semanas para edad; fecha calendario para fecha de floración | Ausente del contrato actual; propuesta para una versión futura | Pendiente | Pendiente |
| `acopio_id` | Equipo 3 | string | No aplica | Presente como requerido en la operación | Pendiente | Por registro operativo según ejemplo; historial y frecuencia pendientes |
| `tiempo_acarreo_min` | Equipo 3 | int | minutos | Presente como requerido en la operación | Pendiente | Por parcela según documentación; cobertura histórica pendiente |
| `medio_acarreo` | Equipo 3 | enum (`cable_via`, `traccion_animal`, `otro`) | No aplica | Presente como requerido en la operación | Pendiente | Por parcela según contrato; cobertura histórica pendiente |
| `capacidad_medio_racimos` | Equipo 3 | int | racimos por viaje | Presente como requerido en la operación | Pendiente | Por parcela según contrato; cobertura histórica pendiente |
| `vehiculos[].capacidad_racimos` | Equipo 3 | int | racimos | Presente en la lista de vehículos del contrato | Pendiente | Disponibilidad por periodo indicada por la documentación; periodos reales pendientes |
| `ventana_despacho.inicio` y `.fin` | Equipo 3 | timestamps | fecha y hora; zona horaria no especificada | Presente como requerido en la operación | Pendiente | Ventana por periodo según contrato; serie histórica y frecuencia de publicación pendientes |
| `inventario[].insumo` | Equipo 3 | string | No aplica | Presente en el arreglo de inventario del contrato | Pendiente | Por parcela según la tabla del contrato; cobertura histórica pendiente |
| `inventario[].cantidad` / `cantidad_disponible` | Equipo 3 | numérico; el modelo almacena `Numeric(10, 2)` y la aplicación lo recibe como `float` | **Unidad física no definida**; confirmar por cada insumo | El contrato muestra una cantidad numérica, sin especificar unidad ni periodo o marca temporal en el ejemplo | Pendiente | La base de datos modela periodo; el contrato de integración no lo incluye en el objeto de ejemplo. Periodo, cobertura, frecuencia y actualidad reales pendientes |
| `consumos[].insumo`, `.periodo`, `.cantidad` | Equipo 3 | `consumos[]` es opcional; el ejemplo incluye insumo string, periodo y cantidad numérica | Unidad física no definida; confirmar por cada insumo | Opcional en el contrato | Pendiente | El ejemplo incluye un periodo; longitud del histórico y cobertura temporal pendientes |
| Histórico de cosecha real por parcela/semana | Unibán, vía Equipo 3 o directamente; canal no confirmado | Tipo y formato no especificados | No definida; se esperaría volumen de cosecha, por confirmar | No forma parte de una entrega confirmada en el repositorio | Pendiente; riesgo registrado en `CONTEXT.md` §11 | Pendiente |
| Estacionalidad (clima, precio) | No hay fuente responsable acordada | Tipo y formato no especificados | No definida | No incluida en el contrato actual | Pendiente | Pendiente |

## Confirmaciones pendientes para inventario

- **Unidades físicas:** confirmar qué representa una unidad de cantidad para cada insumo
  (cajas, cartón y bolsas). No inferirlas de los coeficientes configurados.
- **Cobertura temporal:** confirmar desde qué fecha hasta qué fecha existe información y
  si la cobertura es continua por periodo, parcela e insumo.
- **Frecuencia y actualidad:** confirmar cada cuánto se actualiza el inventario y qué
  fecha/hora representa el saldo entregado (corte o última actualización).
- **Dato ausente frente a cero:** acordar cómo distinguir “inventario conocido igual a
  cero” de “no se recibió inventario para este insumo/parcela/periodo”. D-008 establece
  como propuesta que el Equipo 3 es la fuente de verdad, pero no resuelve esta semántica.
- **Periodo en el contrato:** el modelo de base de datos registra `periodo` para
  inventario; el contrato de integración incluye inventario por insumo y parcela, pero
  el ejemplo no incluye periodo. Confirmar el campo y su significado antes de asumir
  equivalencia entre ambos.

## Parámetros de consumo configurados (no son mediciones de inventario)

`config/parametros.yaml` define los coeficientes `cajas: 0.85`, `carton: 0.85` y
`bolsas: 1.00` bajo `consumo_unitario`. Sus fuentes están marcadas `PENDIENTE`; son
parámetros de consumo por racimo y no cantidades de inventario recibidas del Equipo 3.
La unidad física correspondiente a cada coeficiente también requiere confirmación.

La implementación de `app/core/insumos/estimacion.py` recibe el inventario como mapa
numérico en tiempo de ejecución y calcula requeridos, déficits y excedentes; no obtiene
los saldos de inventario desde este archivo YAML.

## Lectura para T-14 (modelo predictivo)

Con lo documentado no hay histórico de cosecha real confirmado. `consumos[]` es un
histórico opcional de consumo de insumos, no histórico de volumen de cosecha. La edad
de racimo, señalada como variable relevante en TAREAS.md, tampoco está en el contrato
actual.

**Conclusión provisional:** hasta que se confirme una fuente real, T-14 debe tratarse
como escenario de riesgo conforme a D-006; los datos sintéticos deben declararse como
tales. Esta conclusión no sustituye la verificación exigida por T-04.
