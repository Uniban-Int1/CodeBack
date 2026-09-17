# TAREAS.md — Reparto y desglose

> Cada bloque `### T-xx` es una tarea lista para convertirse en issue de GitHub.
> Formato sugerido de issue: **título** = el del bloque, **cuerpo** = el resto, **etiqueta** = el frente, **asignado** = el responsable.

---

## Reparto: dos frentes, dos parejas

| Frente | Pareja | De qué son dueños |
|---|---|---|
| **Backend — lógica de dominio** | **Camilo Mosquera** y **Lizbeth Espinosa** | Proyección de cosecha, motor de programación de recolección y transporte, derivación de insumos, casos de cálculo y evaluación |
| **Front y plataforma** | **David Arango Pineda** y **José Miguel Correa Sánchez** | Modelo de datos y migraciones, API REST, contrato OpenAPI, integración con los equipos 1 y 3, vistas Jinja2, Docker y CI |

### Una advertencia sobre el equilibrio

Con Jinja2 elegido como front (D-001), **las plantillas solas no son medio proyecto**: son quizá el 15 % del trabajo. Para que la pareja de front tenga una mitad real, se lleva también **todo lo que rodea al núcleo**: la capa de datos, la API, la integración con los otros dos equipos y la infraestructura.

Dicho de otro modo: Camilo y Lizbeth construyen **lo que el sistema decide**; David y José Miguel construyen **por dónde entra y sale esa decisión**. Cada mitad se puede trabajar en paralelo porque se tocan solo en dos puntos: el esquema de datos (T-02) y las firmas de las funciones del núcleo, que se acuerdan en la semana 6 y no se mueven sin avisar.

### Dentro de cada pareja

- **Camilo** carga la proyección (determinista y predictiva); **Lizbeth** carga el motor de programación y los insumos.
- **David** carga datos, migraciones, infraestructura y vistas; **José Miguel** carga API, contrato e integración.
- Programen en pareja las tareas marcadas **[par]**: son las que más se benefician de cuatro ojos.

### Reglas del equipo

1. Nadie hace merge de su propio PR. La revisión la hace alguien **de la otra pareja** — así nadie pierde de vista lo que pasa al otro lado.
2. Rama por tarea: `T-10-heuristica-programacion`.
3. Toda decisión técnica que cambie el rumbo se anota en `DECISIONES.md` en el mismo PR.
4. Si una tarea se bloquea más de dos días, se lleva a la sesión de seguimiento. No se espera en silencio.
5. Las firmas de `app/core/**` son **contrato interno**: si cambian, se avisa a la otra pareja antes de hacer merge.

---

# FRENTE BACKEND — Camilo y Lizbeth

## Semana 5–6 · Fundación

### T-04 — Inventario de variables disponibles y faltantes
**Camilo** · **Bloquea:** T-06, T-14

Revisar qué trae realmente el histórico de Unibán y qué falta. Documentar los huecos. Es el insumo para decidir si el modelo predictivo es viable.

*Hecho cuando:* existe una tabla de variables con disponibilidad, tipo y cobertura temporal.

---

### T-05 — Levantar parámetros de acarreo y ventanas
**Lizbeth** · **Con:** José Miguel (que los pide al Equipo 3)

Conseguir tiempos de acarreo, capacidad por medio, capacidad de vehículos y cómo se definen las ventanas. Dejarlos en `config/parametros.yaml`, **no en el código**.

*Hecho cuando:* cada valor del archivo tiene su procedencia anotada; lo que no se consiguió queda marcado `PENDIENTE`, no inventado.

---

### T-06 — Proyección determinista de cosecha `[par]`
**Camilo** · **Archivo:** `app/core/proyeccion/base.py` · **Depende de:** T-04

A partir del aforamiento y la edad de racimo, estimar volumen esperado por parcela y semana. Sin machine learning.

*Hecho cuando:* dado un aforamiento de muestra, devuelve una proyección semanal reproducible.

---

## Semana 6–8 · El modelo base

### T-07 — Cálculo de fecha límite de corte
**Lizbeth** · **Archivo:** `app/core/programacion/fechas.py`

`fecha_limite = ventana − tiempo_empaque − tiempo_acarreo`. Es la pieza más pequeña y la más importante: todo el plan se deduce de aquí.

*Hecho cuando:* hay pruebas del caso normal, del caso en que la ventana ya pasó y del caso de acarreo mayor que la ventana.

---

### T-08 — Derivación de insumos de empaque
**Lizbeth** · **Archivo:** `app/core/insumos/estimacion.py`

`necesidad[i] = volumen × consumo_unitario[i] − inventario[i]` para cajas, cartón y bolsas. Coeficientes configurables por productor.

*Hecho cuando:* cambiar un coeficiente en configuración cambia el resultado sin tocar código.

---

### T-09 — Los 10 a 15 casos de cálculo verificados a mano `[par]`
**Camilo y Lizbeth** · **Carpeta:** `tests/casos/`

Casos con respuesta conocida, calculada a mano **antes** de escribir el código: entradas, resultado esperado y el porqué. Son el criterio de validación de la etapa 2 y la defensa más fuerte ante el profesor.

*Hecho cuando:* `pytest tests/casos/` pasa y cada caso tiene su cálculo a mano escrito en el docstring.

---

## Semana 8–11 · El núcleo

### T-10 — Heurística de programación de recolección y transporte `[par]`
**Lizbeth**, con Camilo · **Archivo:** `app/core/programacion/heuristica.py` · **Es el corazón del proyecto**

Los cuatro pasos de `CONTEXT.md` §8: calcular fechas límite, ordenar por urgencia, asignar carga a vehículos hasta capacidad, reasignar lo que no alcanza.

*Hecho cuando:* sobre instancias pequeñas de solución conocida, el plan respeta capacidad y ventana en el 100 % de los casos.

> Esta es la tarea de la que depende la nota. Prográmenla en pareja.

---

### T-14 — Modelo predictivo de proyección
**Camilo** · **Archivo:** `app/core/proyeccion/predictivo.py` · **Depende de:** T-04, T-06

Regresión con partición temporal y validación cruzada de series de tiempo. Variables: edad de racimo (8–13 semanas), aforamiento, estacionalidad, consumos observados.

*Hecho cuando:* hay métricas registradas comparando contra el modelo base **y** contra una línea base ingenua.
*Nota:* **si no supera a ambos, no se adopta** (D-003). Se conserva el determinista y se documenta por qué. Eso no es un fracaso, es el resultado.

---

## Semana 13–16 · Evaluación

### T-18 — Escenario 1: operación normal
**Lizbeth**

Medir cumplimiento de ventana, uso de capacidad y error de estimación de insumos.

---

### T-19 — Escenario 2: retraso o cierre de una ventana de despacho
**Lizbeth** · **Es el escenario que el profesor va a preguntar**

Mover la ventana y verificar que el plan se recalcula de forma coherente y trazable.

*Hecho cuando:* se puede mostrar el antes y el después con las métricas de ambos.

---

### T-20 — Reporte de evaluación
**Camilo**

Consolidar todas las métricas en un documento con tablas y gráficas.

---

# FRENTE FRONT Y PLATAFORMA — David y José Miguel

## Semana 5–6 · Fundación

### T-01 — Acordar el contrato de integración con los equipos 1 y 3
**José Miguel** · **Bloquea:** T-02, T-11, T-16 · **Primera tarea de todo el proyecto**

Reunirse con los equipos 1 y 3 y cerrar por escrito qué campos, en qué formato y por qué medio se intercambian. Publicar el resultado en `docs/contrato-integracion.md` y marcarlo como `v1`.

*Hecho cuando:* los tres equipos tienen el mismo documento y cada uno puede leer un archivo de muestra del otro.

> El borrador ya está escrito y los cinco puntos pendientes ya tienen una propuesta provisional
> (D-007 a D-011 en `DECISIONES.md`), para no bloquear T-02 y T-06. Falta la confirmación real
> con los equipos 1 y 3 en sesión de seguimiento — sin eso, el contrato sigue siendo "v1 propuesta",
> no un acuerdo cerrado. El más peligroso sigue siendo el formato del `parcela_id`: si los equipos
> 1 y 3 no confirman `P-NNN`, la semana 12 se convierte en un problema.

---

### T-02 — Modelo entidad-relación y esquema de base de datos `[par]`
**David** · **Depende de:** T-01 · **Bloquea:** casi todo

Diagramar las entidades de `CONTEXT.md` §6, revisarlas con los otros dos equipos y con la pareja de backend, e implementarlas en SQLAlchemy con migraciones Alembic.

*Hecho cuando:* `alembic upgrade head` crea el esquema completo en una base limpia.

---

### T-03 — Levantar el entorno: Docker, docker-compose y variables
**David**

`docker compose up` debe levantar PostgreSQL y la app.

*Hecho cuando:* un integrante que clona el repo por primera vez lo levanta siguiendo solo el README.

---

## Semana 8–11 · API y persistencia

### T-11 — Endpoints de ingesta (equipos 1 y 3)
**José Miguel** · **Archivo:** `app/api/ingesta.py` · **Depende de:** T-01, T-02

Recibir aforamientos y datos operativos. Validar con Pydantic y rechazar con mensajes claros lo que no cumple el contrato.

*Hecho cuando:* un payload de muestra de cada equipo entra y queda persistido.

---

### T-12 — Endpoints de consulta: plan, insumos, déficit y supuestos
**José Miguel** · **Archivos:** `app/api/planes.py`, `app/api/insumos.py`

*Hecho cuando:* la especificación OpenAPI generada es suficiente para que otro equipo consuma el servicio sin preguntarnos nada.

---

### T-13 — Persistencia del plan y trazabilidad
**David** · **Con:** José Miguel

Guardar plan, ítems y requerimientos con su `version_metodo`. De un plan se tiene que poder volver a las entradas que lo produjeron (D-005).

*Hecho cuando:* se puede reconstruir el origen de cualquier ítem de un plan guardado.

---

## Semana 11–13 · Vista e integración

### T-15 — Vista del plan de recolección
**David** · **Carpeta:** `app/templates/`

Plantillas Jinja2: plan por día y vehículo, requerimiento de insumos por fecha, déficit frente a inventario. Es un reporte de apoyo a decisión, no un tablero en tiempo real.

*Hecho cuando:* alguien que no programó puede leer el plan de una semana y entender qué hacer.

---

### T-16 — Clientes de integración con los equipos 1 y 3
**José Miguel** · **Carpeta:** `app/integracion/`

Consumir sus servicios de verdad. Manejar los fallos previstos: aforamiento ausente, inventario desactualizado, servicio caído.

*Hecho cuando:* con el servicio del otro equipo apagado, el nuestro degrada de forma controlada y lo dice, en vez de romperse.

---

### T-17 — Prueba de integración conjunta (semana 12) `[par]`
**José Miguel y David** · **Con:** los equipos 1 y 3 · **Fecha fija**

Un aforamiento real del Equipo 1 y un inventario real del Equipo 3 generan un plan consultable que el Equipo 3 recibe en el formato acordado.

*Hecho cuando:* los tres equipos lo ejecutan juntos y queda registrado con evidencia.

---

## Semana 13–16 · Cierre

### T-21 — README reproducible
**David** · **Criterio de validación de la etapa 5**

*Hecho cuando:* **una persona externa al equipo** reproduce un plan siguiendo únicamente el README. Prueben con alguien de otro equipo, de verdad.

---

### T-23 — Video de demostración
**José Miguel**

Demostración reproducible del componente funcionando de extremo a extremo.

---

# AMBOS FRENTES

### T-22 — Informe final en formato IEEE
**Los cuatro** · **Fecha límite: 16 de noviembre de 2026**

Máximo 6 páginas, PDF, con aval previo del profesor. **Sin aval, la nota de este apartado es 0.0.**

Reparto sugerido, alineado con quién construyó qué: Lizbeth escribe el método de programación, Camilo el de proyección y los resultados, José Miguel la arquitectura e integración, David el modelo de datos y las conclusiones.

---

## Puntos de contacto entre las dos parejas

Son solo dos. Si se respetan, las parejas trabajan sin bloquearse.

| Punto | Cuándo se fija | Quién decide |
|---|---|---|
| **Esquema de datos** (T-02) | Semana 6 | David propone, la pareja de backend revisa antes del merge |
| **Firmas de `app/core/**`** | Semana 6 | La pareja de backend propone, José Miguel confirma que la API puede consumirlas |

Mientras esas dos cosas estén acordadas, backend puede trabajar con datos en memoria y la pareja de front puede trabajar con funciones que devuelven valores fijos, sin esperarse.

---

## Orden de recorte si se atrasan

Decidido de antemano, para no improvisar bajo presión:

1. **Primero cae T-14** (modelo predictivo). La proyección determinista alimenta igual al motor.
2. **Después cae la sofisticación de T-15** (la vista puede quedar en una tabla simple).
3. **Nunca se recortan** T-10 (motor de programación), T-01 (contrato) ni T-17 (prueba de integración): de eso dependen los otros dos equipos.
