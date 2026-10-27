# DECISIONES.md — Registro de decisiones técnicas

> Evidencia exigida por la guía del curso: *"Registro de decisiones técnicas y cambios de alcance"*.
> Se actualiza **en el mismo PR** que introduce la decisión. No se escribe al final del semestre.

Formato: una entrada por decisión, con fecha, quién decidió, qué se descartó y por qué.
Una decisión revertida no se borra: se marca como superada y se enlaza la que la reemplaza.

---

## D-001 · Frontend en Jinja2, no React
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** EN REVISIÓN — contradicha por el código actual

Las plantillas Jinja2 viven dentro del mismo servicio FastAPI.

**Se descartó (en su momento):** React como proyecto separado.

**Por qué (en su momento):** React exige un segundo proyecto con build, manejo de estado y capa de
consumo de la API — un sistema adicional que mantener en las tres semanas asignadas a esa etapa.
El entregable es un reporte de apoyo a decisión, no una aplicación interactiva; la guía pide "una
vista o reporte". Con Jinja2 no hay nada que compilar y el despliegue es uno solo.

**Si se necesitan gráficas:** Chart.js por CDN sobre las mismas plantillas, sin cambiar la arquitectura.

**⚠️ Contradicción detectada (octubre de 2026):** el repositorio ya contiene `frontend/`, una app
Expo/React Native completa (`App.js`, 958 líneas, con `package.json`, `app.json`, `eas.json`).
Las plantillas Jinja2 (`app/templates/`) también siguen existiendo y en uso (`app/api/vistas.py`).
No queda registro en este archivo de quién decidió agregar React Native ni por qué se dejó de
respetar esta decisión. **El equipo necesita decidir explícitamente uno de dos caminos:**
mantener ambos frontends con un propósito distinto cada uno (Jinja2 como reporte de apoyo a
decisión, React Native como demo interactiva), o declarar esta decisión superada y documentar
por qué. Mientras no se resuelva, hay una contradicción visible entre este documento y el código
para cualquiera que revise el repositorio — incluido el profesor.

---

## D-002 · Heurística constructiva, no solucionador exacto de ruteo
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

El motor de programación usa una heurística de cuatro pasos (ver `CONTEXT.md` §8).

**Se descartó:** formular y resolver el VRPTW exacto, como en Jiang et al. (2018) con CPLEX.

**Por qué:** el objetivo del semestre es un sistema funcional y verificable, no un récord de
optimalidad. Conservamos las mismas restricciones del modelo de referencia —capacidad de carga
y ventana de despacho— pero con un método que corre en segundos, que el productor puede auditar
y que se valida contra instancias pequeñas de solución conocida.

**Consecuencia:** el solucionador exacto queda documentado como extensión futura. **No se promete.**

---

## D-003 · El modelo predictivo solo se adopta si supera al modelo base
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

El modelo de scikit-learn reemplaza a la proyección determinista **únicamente** si mejora de forma
medible al modelo base **y** a una línea base ingenua, sobre un conjunto de prueba con partición temporal.

**Por qué:** sin línea base no hay forma honesta de afirmar que el modelo predictivo sirvió
(Hyndman y Athanasopoulos, 2021). Poner un modelo complejo solo para poder decir que hay un modelo
es un resultado peor que no ponerlo.

**Si no lo supera:** se conserva el determinista, se documenta aquí la razón y se reporta como
hallazgo en el informe final. Eso no es un fracaso del proyecto, es el resultado del experimento.

---

## D-004 · Los parámetros del dominio no van en el código
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

Tiempos de acarreo, capacidades por medio de transporte, tiempos de empaque y coeficientes de
consumo de insumos viven en `config/parametros.yaml`.

**Por qué:** cada productor tiene condiciones distintas, y el sistema debe adaptarse sin
recompilarse. Además, la guía exige "documentar supuestos y parámetros configurables".

**Regla adicional:** cada valor del archivo debe indicar su procedencia. Un valor sin fuente
se marca como `PENDIENTE`, no se deja disfrazado de dato.

---

## D-005 · Toda recomendación viaja con su versión de método
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

Cada plan y cada requerimiento de insumos lleva el campo `version_metodo`.

**Por qué:** es lo que hace la salida trazable. Sin ese campo, un número entregado al Equipo 3 es
un número suelto del que no se puede reconstruir el origen. Con él, se puede volver desde una
recomendación hasta las entradas y el método que la produjeron — uno de nuestros criterios de validación.

---

## D-006 · Escenarios sintéticos, si los hay, se declaran como tales
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

Si no llega el histórico de Unibán, la evaluación se hace con datos sintéticos **nombrados con el
prefijo `sintetico_` y declarados explícitamente en todo reporte**.

**Por qué:** presentar datos simulados como validación productiva real invalidaría el resultado
académicamente. El riesgo ya está declarado en el anteproyecto; lo que cambia es el instrumento
de prueba, no el alcance.

---

## D-007 · Formato del `parcela_id`: `P-NNN`
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** superada por D-016

Prefijo `P-` seguido de tres dígitos consecutivos, asignado por el Equipo 1 al registrar el
aforamiento inicial de una parcela.

**Por qué (en su momento):** es el campo que más riesgo tiene según T-01: si cada equipo lo
genera con una convención distinta, la prueba de integración de la semana 12 se convierte en un
problema de reconciliación de identificadores en vez de una prueba del sistema.

**Qué pasó:** en la integración real, el Equipo 3 identifica cada parcela con un UUID generado
por su propio sistema, no con `P-NNN`. Ver D-016.

---

## D-008 · El Equipo 3 es la única fuente de verdad del inventario
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** propuesta — pendiente de validar con equipos 1 y 3

Nuestro sistema **lee** inventario del Equipo 3 pero nunca lo escribe ni lo corrige.

**Por qué:** con dos sistemas afirmando el mismo inventario, un desfase entre ellos no tiene
forma honesta de resolverse. Con una sola fuente de verdad, un déficit reportado siempre se
puede rastrear a un único origen.

---

## D-009 · Ventanas de despacho con mínimo 48 h de anticipación
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** propuesta — pendiente de validar con equipos 1 y 3

El Equipo 3 publica cada ventana con al menos 48 h antes de su inicio. Si cambia con menos
margen, el plan ya generado no se recalcula solo — queda como excepción trazada para revisión manual.

**Por qué:** recalcular automáticamente sobre una ventana movida a última hora puede generar un
plan que ya no es físicamente ejecutable (acarreo y empaque no caben). Es preferible una alerta
explícita a un plan silenciosamente inválido.

---

## D-010 · Autenticación entre servicios por token compartido
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** propuesta — pendiente de validar con equipos 1 y 3

Token compartido por variable de entorno (`INTEGRACION_TOKEN`), enviado en cabecera
`Authorization: Bearer`.

**Por qué:** el alcance es académico y los tres equipos operan sobre la misma red de proyecto;
levantar infraestructura de red privada o un proveedor de identidad es un sistema adicional que
no aporta a los criterios de validación del curso.

---

## D-011 · Parcela sin aforamiento se excluye, no se estima a ciegas
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** propuesta — pendiente de validar con equipos 1 y 3

Si el motor de programación necesita una parcela que el Equipo 1 no ha aforado en el periodo,
esa parcela se excluye de la proyección y de la programación. Se informa en un reporte separado
de `item_plan`, con su `parcela_id` y `motivo: "sin_aforamiento"`. No se inventan fecha de corte,
carga estimada ni otros datos, y el resto de las parcelas válidas sigue su flujo normal.

**Por qué:** inventar un aforamiento rompe la trazabilidad (D-005) y puede generar una fecha de
corte y una asignación de vehículo sobre un supuesto falso. Es preferible declarar el hueco que
disfrazarlo de dato. Este reporte separado evita introducir valores ficticios en los campos
obligatorios de `item_plan`; no requiere cambios al esquema de PostgreSQL.

---

## D-012 · Inventario negativo se rechaza con error
**Fecha:** octubre de 2026 · **Decidió:** Camilo (backend) · **Estado:** vigente

El inventario negativo se rechaza con error, no se asume cero.

**Por qué:** dato inválido del Equipo 3; corregirlo rompe trazabilidad (D-005 y D-008).

---

## D-013 · Excedente de insumos explícito
**Fecha:** octubre de 2026 · **Decidió:** Camilo (backend) · **Estado:** vigente

El excedente de insumos es explícito, no queda implícito en déficit cero.

**Por qué:** el objetivo de negocio es evitar tanto faltantes como sobrantes (cajas, cartón, bolsas).

---

## D-014 · Servicio como frontera de parámetros del dominio
**Fecha:** octubre de 2026 · **Decidió:** Camilo (backend) · **Estado:** vigente

`version_metodo` se toma de `metodo` de la proyección. `servicio.py` es la única capa que lee
`parametros()`, manteniendo el core como funciones puras.

---

## D-015 · Metodología para evaluar el error de estimación de insumos
**Fecha:** 12 de octubre de 2026 · **Decidió:** no identificado · **Estado:** vigente

**Objetivo:** evaluar el error de estimación de insumos comparando la cantidad requerida
estimada con el consumo realmente observado, como parte de T-18.

**Fórmula:** el error absoluto es el valor absoluto de la diferencia entre la cantidad
requerida estimada y el consumo observado:
`|cantidad_requerida_estimada - consumo_observado|`.

**Granularidad y emparejamiento:** la unidad de evaluación es insumo, parcela y periodo. El
error solo se calcula cuando las claves permiten emparejar los datos inequívocamente, el
periodo representa el mismo intervalo y las unidades físicas son compatibles. No se permiten
emparejamientos temporales aproximados sin una regla aprobada.

**Unidades:** no se inventan conversiones. Las observaciones cuyas unidades físicas no sean
compatibles se identifican como no comparables y no se incluyen en el cálculo.

**Datos ausentes y observaciones no comparables:** un consumo observado igual a cero es válido
y puede evaluarse si las demás condiciones de comparación se cumplen. Un consumo ausente no se
sustituye por cero y se reporta por separado como no evaluable. Las claves incompletas, los
periodos no emparejables y las unidades incompatibles se identifican por separado como
observaciones no comparables.

**Presentación y agregación:** mostrar los resultados por insumo, parcela y periodo cuando sea
posible evaluarlos. Informar por separado las cantidades evaluables, no evaluables por consumo
ausente y no comparables. No sumar errores correspondientes a unidades físicas diferentes. No
se define una agregación estadística general adicional sin una decisión posterior.

**Validación:** las pruebas sintéticas verifican el comportamiento técnico con resultados
calculables manualmente, pero no demuestran desempeño real. La validación con datos reales
requiere acceso autorizado a datos de Unibán y confirmar unidades, claves, cobertura y
correspondencia temporal.

**Impacto técnico:** antes de modificar entidades o persistencia, se comprobará si las claves
necesarias pueden recuperarse de forma fiable del contexto existente. El modelo persistido solo
se modificará si se demuestra que es necesario.

**Por qué:** el error absoluto conserva la unidad física del insumo y permite evaluar un
consumo observado igual a cero; no distingue por sí solo entre sobreestimación y subestimación.
El error absoluto porcentual no está definido cuando el consumo observado es cero y puede
resultar muy grande cuando el observado es pequeño. T-18 solicita medir el error de estimación;
D-004 establece que los coeficientes de consumo son configurables y D-013 hace explícito el
excedente de insumos, pero ninguna define esta métrica. La fórmula aprobada evalúa cantidad
requerida frente a consumo observado y no reemplaza la medición de déficit o excedente.

---

## D-016 · `parcela_id` es el identificador del sistema de origen, no un formato propio (reemplaza D-007)
**Fecha:** octubre de 2026 · **Decidió:** el equipo · **Estado:** vigente

`parcela_id` se acepta como el identificador que ya genera el Equipo 1 o el Equipo 3 al
registrar la parcela — en la práctica, un UUID. Dejamos de exigir el formato `P-NNN` propuesto
en D-007.

**Se descartó:** pedirle a los equipos 1 y 3 que adoptaran el prefijo `P-NNN`.

**Por qué:** nosotros no generamos `parcela_id`, solo lo recibimos. El código ya lo trata como
un `string` libre en todos los puntos (modelo de datos, esquemas Pydantic de ingesta/planes/
recomendación, endpoints) — ninguno de ellos valida el formato `P-NNN`, así que no había ningún
costo real en mantenerlo como requisito. Exigirles un formato propio a los equipos 1 y 3 les
genera trabajo de mapeo sin beneficio: es más barato para los seis subproyectos que todos usen
el identificador que ya existe en el sistema de origen.

**Consecuencia:** se actualizan los ejemplos de `docs/contrato-integracion.md`,
`docs/modelo-datos.md`, `docs/inventario-variables.md` y `CONTEXT.md` para mostrar un UUID en
lugar de `P-018`. Pendiente: confirmar con el Equipo 1 que el `parcela_id` que registra en el
aforamiento es el mismo valor que usa el Equipo 3, para que los tres equipos refieran la misma
parcela con el mismo identificador — ese es el riesgo real que D-007 señalaba, y sigue vigente
independientemente del formato.

---

## D-017 · El endpoint /recomendar ya no inventa valores por defecto cuando falta un dato obligatorio
**Fecha:** octubre de 2026 · **Decidió:** el equipo · **Estado:** vigente

`SolicitudRecomendacion` (`app/schemas/recomendacion.py`) dejó de rellenar en silencio
`periodo`, `num_plantas_estimado`, `calidad_confianza`, `inventario` y `ventana_despacho`
cuando el Equipo 3 no los envía. Ahora responde `422` con la lista de los campos faltantes.

**Se descartó:** mantener los defaults automáticos (periodo `"2026-W38"`, 1850 plantas,
inventario fijo, ventana `06:00-16:00` de una fecha fija) que traía la implementación anterior.

**Por qué:** violaba la regla 4 del contrato de integración ("si falta un dato de entrada, el
sistema responde qué falta, no se cae ni inventa el valor"). Generar una recomendación con
datos ficticios sin que ningún equipo se entere es peor que rechazar la solicitud con un mensaje
claro — sobre todo porque la fecha límite de corte y el requerimiento de insumos dependían
directamente de esos valores inventados.

**Consecuencia:** las solicitudes del Equipo 3 que no incluyan `ventana_despacho` (su payload
real de hoy no la trae) van a empezar a fallar con `422` en cuanto se despliegue este cambio.
Se les avisa antes de desplegar, para coordinar el momento. El único default que se conserva es
`tiempo_acarreo_min` (cable vía estándar, 35 min) porque no afecta la queja original y no es un
dato que cambie el resultado de forma tan crítica como los demás.

---

## D-018 · Autenticación entre servicios activable sin romper la integración en curso
**Fecha:** octubre de 2026 · **Decidió:** el equipo · **Estado:** vigente — implementa D-010

Se agrega `app/core/seguridad.py` con una verificación de token (`Authorization: Bearer
<INTEGRACION_TOKEN>`), pero la verificación solo se activa si la variable de entorno
`INTEGRACION_TOKEN` está configurada en el entorno de despliegue.

**Por qué:** D-010 ya había decidido que debía existir autenticación, pero activarla de golpe
en el servicio que el Equipo 3 ya está consumiendo en producción cortaría su integración sin
aviso. Con la verificación apagada por defecto, el código queda listo para activarse el día que
se coordine con los equipos 1 y 3, sin otro despliegue de por medio.

**Consecuencia:** mientras `INTEGRACION_TOKEN` no esté configurado en Render, el endpoint sigue
aceptando peticiones sin autenticación — igual que hoy. Activar la variable es, a propósito, una
decisión operativa separada de este cambio de código.

---

<!--
## D-00X · Título de la decisión
**Fecha:** · **Decidió:** · **Estado:** vigente | superada por D-00Y

Qué se decidió.

**Se descartó:** la alternativa.

**Por qué:** la razón.

**Consecuencia:** qué implica para el resto del sistema.
-->
