# Datos

## Procedencia y licencia

Toda fuente de datos usada en el proyecto debe quedar registrada aquí con:
procedencia, licencia o autorización de uso, fecha de obtención y responsable.
Es una evidencia exigida por la guía del curso.

**No hay datos reales de Unibán en el proyecto** (D-019): el acceso al histórico no llegó, así
que `data/historico/` no existe y toda evaluación usa los datos sintéticos de esta tabla.

| Archivo | Procedencia | Licencia / autorización | Fecha | Responsable |
|---|---|---|---|---|
| `tests/casos/*.py` | **Sintético.** Valores escritos a mano en cada caso, con el cálculo esperado en el docstring | Propio del proyecto | sep–oct 2026 | Equipo 2 (backend) |
| `app/core/proyeccion/escenario_sintetico.py` | **Sintético.** 8 parcelas × 24 semanas generadas con semilla 2026 y supuestos explícitos en el módulo | Propio del proyecto | 28/10/2026 | Equipo 2 |
| `scripts/demo_programacion.py` (`PARCELAS_SINTETICAS`) | **Sintético.** 5 parcelas de ejemplo de 4 productores | Propio del proyecto | 28/10/2026 | Equipo 2 |
| `scripts/demo_en_vivo.py` | **Sintético.** Caso base del contrato (1850 plantas, confianza 0.87) | Propio del proyecto | oct 2026 | Equipo 2 |
| `config/parametros.yaml` | Parámetros del dominio. Cada valor cita su fuente (Ordoñez-Avila y Perdomo-Perdomo 2019; Arrieta-Escobar et al. 2026) o queda marcado `PENDIENTE` | Valores de literatura citada; los `PENDIENTE` son supuestos del equipo | sep 2026 | Equipo 2 (T-05) |
| Solicitudes del Equipo 3 en las pruebas de integración | Cargas de ejemplo con identificadores UUID ilustrativos (`docs/pruebas-integracion.md`) | Compartidas por el Equipo 3 para la integración | 27–28/10/2026 | Equipo 3 |

## Reglas

- `data/muestras/` — datos de muestra, sí van al repositorio.
- `data/historico/` — datos reales de Unibán, **NO van al repositorio** (ignorado en `.gitignore`).
- Los escenarios sintéticos deben nombrarse con el prefijo `sintetico_` y declararse como tales
  en cualquier reporte. Nunca se presentan como validación productiva real.
