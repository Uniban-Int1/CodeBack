# DECISIONES.md — Registro de decisiones técnicas

> Evidencia exigida por la guía del curso: *"Registro de decisiones técnicas y cambios de alcance"*.
> Se actualiza **en el mismo PR** que introduce la decisión. No se escribe al final del semestre.

Formato: una entrada por decisión, con fecha, quién decidió, qué se descartó y por qué.
Una decisión revertida no se borra: se marca como superada y se enlaza la que la reemplaza.

---

## D-001 · Frontend en Jinja2, no React
**Fecha:** septiembre de 2026 · **Decidió:** el equipo · **Estado:** vigente

Las plantillas Jinja2 viven dentro del mismo servicio FastAPI.

**Se descartó:** React como proyecto separado.

**Por qué:** React exige un segundo proyecto con build, manejo de estado y capa de consumo de la API
— un sistema adicional que mantener en las tres semanas asignadas a esa etapa. El entregable es
un reporte de apoyo a decisión, no una aplicación interactiva; la guía pide "una vista o reporte".
Con Jinja2 no hay nada que compilar y el despliegue es uno solo.

**Si se necesitan gráficas:** Chart.js por CDN sobre las mismas plantillas, sin cambiar la arquitectura.

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
**Fecha:** septiembre de 2026 · **Decidió:** el equipo (propuesta) · **Estado:** propuesta — pendiente de validar con equipos 1 y 3

Prefijo `P-` seguido de tres dígitos consecutivos, asignado por el Equipo 1 al registrar el
aforamiento inicial de una parcela.

**Por qué:** es el campo que más riesgo tiene según T-01: si cada equipo lo genera con una
convención distinta, la prueba de integración de la semana 12 se convierte en un problema de
reconciliación de identificadores en vez de una prueba del sistema.

**Consecuencia:** hasta que el Equipo 1 lo confirme, es solo una propuesta razonable, no un
acuerdo cerrado.

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

## D-015 · Propuesta metodológica para evaluar el error de estimación de insumos
**Fecha:** pendiente de aprobación · **Decidió:** pendiente de aprobación · **Estado:** propuesta pendiente de aprobación

**Objetivo:** definir cómo evaluar la diferencia entre la cantidad requerida estimada por el
sistema y el consumo observado, para aportar evidencia a T-18.

**Emparejamiento candidato:** relacionar cada observación por insumo, parcela y periodo. Antes
de calcular una métrica, se debe confirmar que esas claves están disponibles y que la fecha
asociada al requerimiento representa el mismo intervalo que el periodo del consumo observado.
No se debe emparejar por aproximación temporal sin una regla acordada.

**Unidades:** solo se compararán cantidades cuando se haya confirmado que la estimación y el
consumo observado usan unidades compatibles para el mismo insumo. Si las unidades no están
confirmadas o no coinciden, la observación se identifica separadamente como no comparable.

**Métrica candidata:** considerar como alternativa inicial el error absoluto:
`|cantidad_requerida_estimada - consumo_observado|`. Esta fórmula no queda aprobada por esta
propuesta. El error absoluto se expresa en la unidad del insumo y no distingue por sí solo entre
sobreestimación y subestimación.

El error absoluto porcentual es otra alternativa, pero no está definido cuando el consumo
observado es cero y puede resultar muy grande cuando el valor observado es pequeño. Su uso
requeriría acordar expresamente el tratamiento de esos casos.

**Datos ausentes y observaciones no comparables:** un consumo observado igual a cero es un valor
observado, no un dato ausente; podrá incluirse si se aprueba una métrica aplicable y las demás
condiciones de comparación se cumplen. Un consumo ausente no se reemplaza por cero y se informa
separadamente como no evaluable. Las observaciones con claves incompletas, periodos no
emparejables o unidades incompatibles también se identifican por separado, sin clasificarlas
como consumos ausentes.

**Presentación y agregación:** conservar los resultados por insumo, parcela y periodo cuando las
claves y unidades permitan compararlos. No sumar errores de insumos con unidades físicas
diferentes. La selección de un resumen agregado, su método y ponderación quedan pendientes de
acuerdo; hasta entonces, presentar los resultados separados por insumo y reportar por separado
las observaciones evaluables, no evaluables por consumo ausente y no comparables.

**Validación:** las pruebas sintéticas verificarán la implementación de la metodología que se
apruebe, con resultados calculables manualmente y datos identificados explícitamente como
sintéticos. No constituyen validación de desempeño con datos reales. La validación posterior
requiere datos reales autorizados de Unibán y la verificación de unidades, claves y
correspondencia temporal.

**Impacto previsto:** la implementación se realizará después de aprobar la metodología. Se
reutilizará el contexto existente para relacionar cada requerimiento con insumo, parcela y
periodo; el modelo persistido solo se modificará si se demuestra que esas relaciones no pueden
recuperarse de forma fiable del contexto existente.

**Por qué:** T-18 solicita medir el error de estimación de insumos, pero no fija fórmula,
unidades compatibles, claves temporales, tratamiento de ausencias ni agregación. El contrato
describe `consumos[]` como opcional y destinado a validación, mientras que las unidades y la
cobertura de esos datos siguen pendientes de confirmación. Esta propuesta explicita los puntos
por resolver sin presentar una fórmula como aprobada.

---

<!--
## D-00X · Título de la decisión
**Fecha:** · **Decidió:** · **Estado:** vigente | superada por D-00Y

Qué se decidió.

**Se descartó:** la alternativa.

**Por qué:** la razón.

**Consecuencia:** qué implica para el resto del sistema.
-->
