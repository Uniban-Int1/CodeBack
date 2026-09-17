# CONTEXT.md — Contexto del proyecto

> Documento de referencia del equipo. Si llegas nuevo al repo, lee esto antes de tocar código.
> Última actualización: septiembre de 2026.

---

## 1. Qué es esto

Software de apoyo a decisiones para **pequeños productores plataneros vinculados a Unibán en el Urabá antioqueño**.

El sistema responde una pregunta operativa concreta:

> ¿Cómo transformar los datos de plantación, producción y operación de un conjunto de pequeños productores plataneros en un **plan de recolección y transporte** —qué parcela se corta, en qué orden se acarrea y con qué vehículo llega la carga al acopio dentro de la ventana de despacho— y en la cantidad de **insumos de empaque** que ese plan requiere?

**El plan de recolección es el producto central. Los insumos se derivan de él, no al revés.**

### Contexto académico

| | |
|---|---|
| Asignatura | Proyecto Integrador I — código 2508700 |
| Grupo | 7 (línea temática: desarrollo de software) |
| Semestre | 2026-2 · Universidad de Antioquia |
| Proyecto mayor | Plátano – Unibán |
| Nuestro subproyecto | Equipo 2 de 3 — Logística de suministros y cosecha |
| Modalidad | **Desarrollo** — debe haber software funcional, verificable y documentado |
| Profesor | David S. Fernández Mc Cann |

### Equipo

| Frente | Pareja |
|---|---|
| Backend — lógica de dominio | Camilo Mosquera · Lizbeth Espinosa |
| Front y plataforma | David Arango Pineda · José Miguel Correa Sánchez |

---

## 2. El dominio: por qué el problema es difícil

Esta sección es la más importante del documento. Sin entenderla, el código no tiene sentido.

### La cadena física

```
  CORTE              ACARREO                ACOPIO              DESPACHO
  en parcela   →     cable vía /      →     empacadora    →     embarque
                     tracción animal        (mismo día)         (ventana fija)
```

1. **Corte.** Se corta el racimo en la parcela.
2. **Acarreo interno.** Los racimos se mueven hasta el sitio de carga por cable vía o tracción animal. Capacidad del orden de **60 a 70 racimos por viaje**, en distancias cercanas a los **800 m**.
3. **Acopio y empaque.** El plátano de exportación **se empaca el mismo día en que se corta**. No hay margen.
4. **Despacho.** La ventana la fija el embarque. Ni el productor ni nosotros la controlamos.

### Las dos restricciones que gobiernan todo

**a) La ventana empuja hacia atrás.** Como se empaca el mismo día del corte, la fecha de corte **no es una decisión libre**: se deduce restando hacia atrás desde la ventana de despacho.

```
fecha_limite_corte = ventana_despacho − tiempo_empaque − tiempo_acarreo
```

**b) La capacidad limita hacia adelante.** El cable vía y el vehículo tienen capacidad finita. No se puede mover todo lo que se quisiera en un solo viaje, y como los productores son pequeños y están dispersos, hay que **consolidar la carga de varios en un mismo recorrido**.

### Por qué importa

El error se paga tres veces:

- Fruta que llega fuera de ventana → se vende como nacional, a menor precio.
- Vehículos que salen a media capacidad → sobrecosto de acarreo.
- Insumos de empaque pedidos con margen de seguridad → unas veces faltan, otras sobran.

En Colombia las pérdidas de perecederos en poscosecha, almacenamiento y transporte se estiman en **40,4 %**, y buena parte de eso es desfase logístico, no biología del producto.

### Cifras de referencia del dominio

| Dato | Valor | Fuente |
|---|---|---|
| Exportación anual de plátano desde Urabá | ~4.000.000 cajas | [6] |
| Pequeños productores independientes vía Unibán | 2.000 – 2.440 | [6] |
| Pérdidas de perecederos (poscosecha + almacenamiento + transporte) | 40,4 % | [4] |
| Capacidad de cable vía por viaje | 60 – 70 racimos | [8] |
| Distancia típica de acarreo interno | ~800 m | [8] |
| Edad de racimo relevante para pronóstico | 8 – 13 semanas | [1] |

### Glosario

| Término | Significado |
|---|---|
| **Aforamiento** | Estimación de cuántas plantas hay en una parcela y en qué estado productivo. Lo produce el Equipo 1. |
| **Racimo** | Unidad de fruta cortada de la planta. |
| **Acarreo** | Movimiento de los racimos desde la parcela hasta el sitio de carga o acopio. |
| **Cable vía** | Sistema de transporte aéreo por cable usado dentro de la finca. |
| **Acopio** | Sitio donde se recibe, selecciona y empaca la fruta. |
| **Ventana de despacho** | Rango de fechas/horas en que la carga debe estar lista para el embarque. |
| **Insumos de empaque** | Cajas, cartón y bolsas. |
| **Parcela** | Unidad productiva de un productor. Es la unidad mínima de planificación. |

---

## 3. Alcance

### Sí hacemos

- Proyección de cosecha por parcela y semana.
- Plan de recolección y transporte: fecha de corte, secuencia de acarreo, asignación de carga a vehículos.
- Derivación de la necesidad de cajas, cartón y bolsas a partir de ese plan.
- Vista de apoyo a decisión y API REST documentada.

### No hacemos

| Fuera de alcance | Responsable |
|---|---|
| Conteo de plantas en campo | Equipo 1 |
| Registro operativo de parcelas, movimientos e inventarios | Equipo 3 |
| Diseño de la red de centros de acopio | — |
| Logística marítima desde el puerto | — |
| Gestión real de flota y contratación del transporte | — |

---

## 4. Objetivos

**General.** Desarrollar y validar un sistema web que genere, para un conjunto de pequeños productores plataneros vinculados a Unibán, un plan semanal de recolección y transporte de cosecha ajustado a las ventanas de despacho, junto con la estimación de los insumos de empaque que ese plan requiere.

**Específicos.**

1. Modelar las variables de entrada (aforamiento, estado productivo, ubicación, tiempo de acarreo, capacidad de transporte, ventanas de despacho, inventario, coeficientes de consumo) y formalizarlas en un esquema de datos y en un contrato de integración acordado con los equipos 1 y 3.
2. Implementar la proyección de cosecha por parcela y periodo mediante un modelo base determinista y un modelo de predicción entrenado con registros históricos, comparando ambos contra una línea base ingenua.
3. Construir el módulo de programación que proponga fecha de corte, secuencia de recolección y asignación de carga respetando capacidad y ventana, y derivar la necesidad de insumos.
4. Evaluar mediante casos verificados manualmente, error de predicción y dos escenarios de contraste, midiendo **cumplimiento de ventana**, **uso de capacidad de transporte** y **déficit de insumos**.

---

## 5. Arquitectura

### Los tres pasos

```
   Equipo 1 ─┐
             ├→  [1] Proyección  →  [2] Plan de recolección  →  [3] Insumos  →  Salida
   Equipo 3 ─┘      de cosecha        y transporte               de empaque      ↓
                                            ↑ ↑                              Equipo 3
                                            │ └── capacidad y acarreo
                                            └──── ventana de despacho
```

### Stack

**Backend**

| # | Tecnología | Para qué |
|---|---|---|
| 1 | Python 3.11+ | Lenguaje único: sirve para el servicio y para la analítica |
| 2 | FastAPI | Servicio web. Genera la especificación OpenAPI del contrato |
| 3 | PostgreSQL | Base de datos. Integridad referencial y consultas por periodo |
| 4 | SQLAlchemy | ORM |
| 5 | Alembic | Migraciones del esquema |
| 6 | pandas | Manejo de los registros históricos |
| 7 | scikit-learn | Modelo predictivo de proyección |
| 8 | pytest | Pruebas, incluidos los casos de cálculo verificados a mano |
| 9 | Docker | Empaquetado y despliegue reproducible |

**Frontend**

Plantillas **Jinja2** renderizadas por el mismo servicio FastAPI. Sin build, sin proyecto aparte, un solo despliegue.
Si más adelante hacen falta gráficas: Chart.js por CDN sobre las mismas plantillas.

> **Decisión cerrada.** No hay React. Ver `DECISIONES.md`.

---

## 6. Modelo de datos (entidades mínimas)

| Entidad | Campos clave |
|---|---|
| `productor` | id, nombre, municipio |
| `parcela` | id, productor_id, area_ha, ubicacion, acopio_id, tiempo_acarreo_min, medio_acarreo, capacidad_medio |
| `acopio` | id, nombre, ubicacion |
| `aforamiento` | id, parcela_id, fecha, num_plantas, calidad_confianza |
| `proyeccion_cosecha` | id, parcela_id, periodo, volumen_esperado, metodo, version_metodo |
| `vehiculo` | id, placa/alias, capacidad, disponible_desde, disponible_hasta |
| `ventana_despacho` | id, periodo, inicio, fin, acopio_id |
| `plan_recoleccion` | id, periodo, generado_en, version_metodo |
| `item_plan` | id, plan_id, parcela_id, fecha_corte, vehiculo_id, orden, carga_estimada, cumple_ventana |
| `insumo` | id, nombre (cajas / cartón / bolsas), unidad |
| `coeficiente_consumo` | id, insumo_id, productor_id, valor_por_unidad_cosecha |
| `inventario` | id, insumo_id, parcela_id, periodo, cantidad_disponible |
| `requerimiento_insumo` | id, plan_id, insumo_id, fecha, cantidad_requerida, deficit |

Detalle completo y diagrama ER en `docs/modelo-datos.md`.

---

## 7. Contrato de integración

Somos **seis subproyectos, no seis islas**. Este equipo publica y versiona la especificación OpenAPI.

### Recibimos del Equipo 1 — Aforamiento

```json
{
  "parcela_id": "P-018",
  "fecha": "2026-09-14",
  "area_ha": 2.4,
  "num_plantas_estimado": 1850,
  "calidad_confianza": 0.87
}
```

### Recibimos del Equipo 3 — Gestión operativa

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

### Entregamos al Equipo 3 — Plan + insumos

```json
{
  "plan_id": "PL-2026-W38",
  "periodo": "2026-W38",
  "version_metodo": "heuristica-v1",
  "items": [
    {"parcela_id": "P-018", "fecha_corte": "2026-09-20",
     "vehiculo_id": "V-3", "orden": 2,
     "carga_estimada_racimos": 210, "cumple_ventana": true}
  ],
  "insumos": [
    {"insumo": "cajas", "fecha": "2026-09-20",
     "cantidad_requerida": 412, "inventario": 300, "deficit": 112}
  ]
}
```

**Reglas del contrato**

- Formato: JSON por API REST. Alternativa aceptada del Equipo 1: CSV versionado.
- Versionado: `v1`, `v2`… Los cambios se acuerdan en sesión de seguimiento.
- Responsable de publicar y versionar: **este equipo**.
- **Prueba de integración conjunta: semana 12**, con datos reales de los equipos 1 y 3.

---

## 8. Cómo se arma el plan (la heurística)

Núcleo del subproyecto. Deliberadamente **no** es un solucionador exacto de ruteo.

```
1. Para cada parcela:
     fecha_limite = ventana_despacho − tiempo_empaque − tiempo_acarreo
2. Ordenar parcelas por fecha_limite (más urgente primero)
3. Asignar carga a los vehículos disponibles hasta agotar capacidad
4. Reasignar lo que no alcanza su ventana
→ salida: fecha de corte, secuencia y vehículo por parcela
```

Y de ahí salen los insumos:

```
necesidad[i] = volumen_del_plan × consumo_unitario[i] − inventario[i]
      donde i ∈ { cajas, cartón, bolsas }
```

> **Por qué heurística y no solucionador exacto:** el objetivo del semestre es un sistema funcional y verificable, no un récord de optimalidad. Conservamos las restricciones del modelo de referencia (capacidad y ventana) pero con un método que corre en segundos, que el productor puede auditar y que se valida contra instancias pequeñas de solución conocida. El solucionador exacto queda documentado como extensión, no prometido.

---

## 9. Criterios de validación

Ninguno depende de nuestra opinión.

| Criterio | Cómo se mide | Meta |
|---|---|---|
| **Cumplimiento de ventana** | % de parcelas programadas que alcanzan su ventana | Reportado por escenario |
| **Uso de capacidad de transporte** | carga asignada / capacidad disponible | Reportado por escenario |
| **Corrección aritmética** | 10–15 casos de cálculo con respuesta conocida | 100 % reproducidos exactamente |
| **Respeto de restricciones** | instancias pequeñas de solución conocida | 100 % respeta capacidad y ventana |
| **Error de predicción** | conjunto de prueba con partición temporal, contra modelo base y línea base ingenua | El predictivo solo se adopta si mejora |
| **Trazabilidad** | de un plan se vuelve a sus entradas y a la versión del método | Verificable |
| **Reproducibilidad** | una persona externa reproduce un plan con solo el README | Logrado |

**Escenarios de contraste obligatorios**

1. Operación normal.
2. **Retraso o cierre de una ventana de despacho** — el fallo real de esta operación.

---

## 10. Decisiones ya tomadas

Ver `DECISIONES.md` para el registro completo con fecha y justificación. Resumen:

- Frontend en Jinja2, no React.
- Heurística constructiva, no solucionador exacto de ruteo.
- El modelo predictivo solo se adopta si supera al modelo base **y** a una línea base ingenua.
- Los coeficientes y parámetros son configurables: **no van dentro del código**.
- La recomendación viaja siempre con su `version_metodo` (trazabilidad).

---

## 11. Riesgo declarado

**Asumimos acceso a los registros históricos de Unibán.**

Si ese acceso no se concreta:

- El motor de programación **no depende de histórico** — funciona con la proyección determinista, la ventana y las capacidades. Sigue en pie.
- Solo se ve afectado el objetivo 2. Se pasa a escenarios sintéticos **declarados explícitamente como tales**, sin presentarlos como validación productiva real.
- Cambia el instrumento de prueba, no el alcance.

---

## 12. Fechas

| Hito | Fecha |
|---|---|
| Contrato de integración aceptado | Semana 6 |
| Módulo determinista con pruebas | Semana 8 |
| Motor de programación + API | Semana 11 |
| **Prueba de integración conjunta** | **Semana 12** |
| Evaluación y documentación | Semana 15 |
| **Entrega informe final (IEEE, PDF, máx. 6 pág.)** | **16 de noviembre de 2026** |
| Sustentación oral | 30 nov – 5 dic de 2026 |

---

## 13. Evidencias que hay que conservar

Exigidas por la guía del curso:

- [x] Repositorio con control de versiones
- [ ] README con instrucciones de ejecución
- [ ] Registro de decisiones técnicas y cambios de alcance (`DECISIONES.md`)
- [ ] Datos de prueba o muestras con procedencia y licencia (`data/README.md`)
- [ ] Pruebas funcionales/técnicas y resultados
- [ ] Video o demostración reproducible del componente

---

## 14. Bibliografía

- [1] Arrieta-Escobar, Paternina-Arboleda, Vélez y García-Llinás, "Enhancing agricultural decision-making: Banana yield forecasting in Colombia using tuned ensemble machine learning models", *AgriEngineering*, 8(7), art. 289, 2026. doi: 10.3390/agriengineering8070289
- [2] Hyndman y Athanasopoulos, *Forecasting: Principles and Practice*, 3.ª ed., OTexts, 2021. https://otexts.com/fpp3/
- [3] Bolívar, Cantillo y Miranda, "Agri-food supply chain design for perishable products: application to small-scale farmers", *Operational Research*, 25(2), art. 26, 2025. doi: 10.1007/s12351-024-00878-x
- [4] Ballesteros Gómez, "Estrategias para la reducción de pérdidas de productos perecederos en el proceso de distribución. Caso de estudio plátano en la región de Cundinamarca", tesis de maestría, Universidad Nacional de Colombia, 2017.
- [5] Zhai, Martínez, Beltran y Martínez, "Decision support systems for agriculture 4.0: Survey and challenges", *Computers and Electronics in Agriculture*, 170, art. 105256, 2020. doi: 10.1016/j.compag.2020.105256
- [6] García Vélez, "Desde Urabá se exportan cerca de 4 millones de cajas de plátano de pequeños productores al año", *Alerta Paisa*, 10 sep. 2025.
- [7] Jiang, Chen y Fang, "Integrated harvest and distribution scheduling with time windows of perishable agri-products in one-belt and one-road context", *Sustainability*, 10(5), art. 1570, 2018. doi: 10.3390/su10051570
- [8] Ordoñez-Avila y Perdomo-Perdomo, "Rediseño del sistema de transporte de racimos de banano para la recolección en el campo", *Revista Tecnología en Marcha*, 32(4), pp. 171–178, 2019. doi: 10.18845/tm.v32i4.4801
- [9] Díaz Gutiérrez, Alfaro Rodríguez y Araya Mora, "Comparación de dos métodos de cosecha y acarreo del banano en Costa Rica", *E-Agronegocios*, 9(1), pp. 1–23, 2023. doi: 10.18845/ea.v9i1.6110