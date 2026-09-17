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

<!--
## D-00X · Título de la decisión
**Fecha:** · **Decidió:** · **Estado:** vigente | superada por D-00Y

Qué se decidió.

**Se descartó:** la alternativa.

**Por qué:** la razón.

**Consecuencia:** qué implica para el resto del sistema.
-->
