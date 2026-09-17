# Modelo de datos

> **Estado:** implementado en `app/models/entidades.py` y `migrations/versions/1c9c07620028_esquema_inicial.py`.
> El esquema sigue siendo revisable con los equipos 1 y 3 — en particular el tipo y formato de
> `parcela_id` (ver D-007) — pero ya no es solo diagrama: `alembic upgrade head` lo crea completo.
> Responsable: David — frente front y plataforma (T-02)

## Diagrama

```
productor ──< parcela ──< aforamiento
                 │
                 ├──< proyeccion_cosecha
                 ├──< inventario >── insumo
                 └──> acopio

vehiculo ──< item_plan >── parcela
                 │
            plan_recoleccion ──< requerimiento_insumo >── insumo

ventana_despacho ──> acopio
coeficiente_consumo >── insumo, productor
```

## Entidades

### productor
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | text | |
| municipio | text | Chigorodó, Belén de Bajirá, Necoclí, Santa María la Antigua del Darién |

### parcela
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | identificador acordado con los equipos 1 y 3 |
| productor_id | FK | |
| area_ha | numeric | |
| ubicacion | text / point | |
| acopio_id | FK | a qué acopio despacha |
| tiempo_acarreo_min | int | de la parcela al acopio — **dato del Equipo 3** |
| medio_acarreo | enum | `cable_via` \| `traccion_animal` \| `otro` |
| capacidad_medio_racimos | int | racimos por viaje |

### aforamiento
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| parcela_id | FK | |
| fecha | date | |
| num_plantas | int | **dato del Equipo 1** |
| calidad_confianza | numeric 0–1 | viaja con la recomendación |

### proyeccion_cosecha
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| parcela_id | FK | |
| periodo | text | ISO week, `2026-W38` |
| volumen_racimos | numeric | |
| metodo | text | `determinista-v1` \| `predictivo-v1` |

### vehiculo
| Campo | Tipo |
|---|---|
| id | PK |
| alias | text |
| capacidad_racimos | int |
| disponible_desde / disponible_hasta | timestamp |

### ventana_despacho
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| acopio_id | FK | |
| periodo | text | |
| inicio / fin | timestamp | **la fija el embarque, no el productor** |

### plan_recoleccion
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| periodo | text | |
| generado_en | timestamp | |
| version_metodo | text | obligatorio — trazabilidad (D-005) |

### item_plan
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| plan_id | FK | |
| parcela_id | FK | |
| fecha_corte | timestamp | deducida hacia atrás desde la ventana |
| vehiculo_id | FK nullable | null si no se pudo asignar |
| orden | int | secuencia de recolección |
| carga_estimada_racimos | int | |
| cumple_ventana | bool | métrica de validación |
| motivo | text nullable | por qué no cumple |

### insumo / coeficiente_consumo / inventario / requerimiento_insumo
| Entidad | Campos |
|---|---|
| insumo | id, nombre (`cajas`, `carton`, `bolsas`), unidad |
| coeficiente_consumo | id, insumo_id, productor_id, valor_por_racimo |
| inventario | id, insumo_id, parcela_id, periodo, cantidad_disponible |
| requerimiento_insumo | id, plan_id, insumo_id, fecha, cantidad_requerida, deficit |

## Validaciones obligatorias

- Cantidades no negativas.
- Fechas coherentes: `fecha_corte` < `ventana.fin`.
- Unidades explícitas: racimos vs. cajas no se mezclan.
- Todo movimiento de inventario debe ser trazable a su origen.
