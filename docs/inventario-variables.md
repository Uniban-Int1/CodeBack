# Inventario de variables — disponibilidad y huecos

> Evidencia de T-04. Insumo para decidir si el modelo predictivo (T-14) es viable con lo que
> realmente entrega Unibán, y para que T-05 sepa qué parámetros puede levantar con dato real
> hoy y cuáles quedan `PENDIENTE` en `config/parametros.yaml`.
> Responsable: Camilo — frente backend.
> **Estado:** el riesgo declarado en `CONTEXT.md` §11 sigue vigente — el acceso al histórico
> real de Unibán aún no se ha concretado. Esta tabla se actualiza en cuanto llegue el primer
> extracto real; hasta entonces, "disponibilidad" se basa en lo acordado en el contrato de
> integración (`docs/contrato-integracion.md`), no en datos ya recibidos.

| Variable | Fuente | Disponibilidad | Tipo | Cobertura temporal | Notas |
|---|---|---|---|---|---|
| `parcela_id` | Equipo 1 / Equipo 3 | Acordada (propuesta D-007), no verificada en dato real | string | — | Ver riesgo del formato en el contrato |
| `num_plantas_estimado` | Equipo 1 (aforamiento) | Acordada, no verificada | int | por aforamiento, no periódica | Insumo directo de T-06 |
| `calidad_confianza` | Equipo 1 (aforamiento) | Acordada, no verificada | float 0–1 | por aforamiento | Obligatoria en el contrato, no opcional |
| `area_ha` | Equipo 1 | Acordada, no verificada | float | por aforamiento | |
| `edad_racimo` (semanas) | Equipo 1 — **no está en el contrato actual** | **Falta** | — | — | La literatura [1] la señala como variable dominante (8–13 semanas); hoy no viaja en el payload de aforamiento. Se propone añadirla en v2 del contrato. |
| `tiempo_acarreo_min` | Equipo 3 | Acordada, no verificada | int | por parcela | |
| `medio_acarreo` / `capacidad_medio_racimos` | Equipo 3 | Acordada, no verificada | enum / int | por parcela | Valores de referencia (60–70 racimos, ~800 m) vienen de literatura [8], no de Unibán todavía |
| `vehiculos[].capacidad_racimos` | Equipo 3 | Acordada, no verificada | int | por periodo | |
| `ventana_despacho` | Equipo 3 | Acordada, no verificada | timestamps | por periodo | Frecuencia de publicación propuesta en D-009 |
| `inventario[]` | Equipo 3 | Acordada, no verificada | float | por periodo | Fuente única de verdad, D-008 |
| `consumos[]` histórico | Equipo 3 | Opcional en el contrato | float | por periodo, histórico | Es lo que alimentaría T-14 si llega con suficiente cobertura |
| Histórico de cosecha real por parcela/semana | Unibán, vía Equipo 3 o directo | **No confirmado** — riesgo declarado en `CONTEXT.md` §11 | — | — | Sin esto, T-14 (modelo predictivo) se evalúa solo con escenarios sintéticos declarados como tales (D-006) |
| Estacionalidad (clima, precio) | Ninguna fuente acordada | **Falta** | — | — | Mencionada como variable posible para T-14 en TAREAS.md; no hay fuente identificada aún |

## Lectura para T-14 (modelo predictivo)

Con lo acordado hasta ahora **no hay histórico de cosecha real** confirmado, solo el compromiso
de que el Equipo 3 puede entregar `consumos[]` (consumo de insumos, no volumen de cosecha) como
histórico opcional. La variable más señalada por la literatura para el pronóstico —edad de
racimo— tampoco está en el contrato actual.

**Conclusión provisional:** T-14 debe planearse asumiendo escenario de riesgo (D-006): entrenar y
validar con datos sintéticos declarados como tales hasta que se confirme una fuente real de
histórico de cosecha. No cambia el alcance del objetivo 2, cambia el instrumento de prueba.

## Huecos a cerrar antes de semana 8 (bloquea T-14)

1. Agregar `edad_racimo` (o la fecha de floración, de la que se deriva) al contrato de
   aforamiento — proponer en la próxima sesión con Equipo 1.
2. Confirmar si Unibán entrega histórico de volumen de cosecha por parcela/semana, y con qué
   cobertura temporal — condición del objetivo 2 completo (`CONTEXT.md` §11).
