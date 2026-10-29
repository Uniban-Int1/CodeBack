# Logística de recolección, transporte e insumos — Plátano / Unibán

Sistema de apoyo a decisiones que genera un **plan semanal de recolección y transporte de cosecha**
ajustado a las ventanas de despacho, y deriva de ese plan la necesidad de insumos de empaque,
para pequeños productores plataneros vinculados a Unibán en el Urabá antioqueño.

Proyecto Integrador I · Grupo 7 · Semestre 2026-2 · Universidad de Antioquia
Plátano – Unibán · Equipo 2 de 3

| | |
|---|---|
| **Contexto completo del proyecto** | [`CONTEXT.md`](CONTEXT.md) — léelo primero |
| **Reparto y tareas** | [`TAREAS.md`](TAREAS.md) |
| **Decisiones técnicas** | [`DECISIONES.md`](DECISIONES.md) |
| **Contrato con los otros equipos** | [`docs/contrato-integracion.md`](docs/contrato-integracion.md) |

---

## Equipo

| Frente | Pareja | Área |
|---|---|---|
| **Backend — lógica de dominio** | Camilo Mosquera · Lizbeth Espinosa | Proyección de cosecha, motor de programación, insumos, evaluación |
| **Front y plataforma** | David Arango Pineda · José Miguel Correa Sánchez | Datos y migraciones, API REST, contrato, integración, app móvil, Docker |

Detalle por persona y tarea en [`TAREAS.md`](TAREAS.md).

---

## Backend desplegado

El backend ya está en producción en Render (plan free, se duerme tras inactividad —
la primera llamada después de un rato puede tardar ~90 s en responder):

- API: https://platano-logistica-api.onrender.com
- Documentación interactiva (Swagger): https://platano-logistica-api.onrender.com/docs

Se despliega automáticamente desde `main` (ver `render.yaml`).

## Cómo levantarlo en local

Requisitos: Docker y Docker Compose.

```bash
git clone <url-del-repo>
cd CodeBack
cp .env.example .env
docker compose up --build
```

La API queda en http://localhost:8000 (sin vista web — ver "App móvil" más abajo).
La documentación interactiva, en http://localhost:8000/docs

### Migraciones

```bash
docker compose exec app alembic upgrade head
```

### Pruebas

```bash
docker compose exec app pytest
docker compose exec app pytest tests/casos -v   # casos de cálculo verificados a mano
```

No hay todavía un script de datos de muestra (`app/seed` no existe); los casos de
prueba en `tests/casos/` construyen sus propios datos sintéticos inline.

---

## Sin Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajustar DATABASE_URL a tu Postgres local
alembic upgrade head
uvicorn app.main:app --reload
```

---

## App móvil (frontend)

`frontend/` es el frontend oficial del proyecto: una app Expo/React Native que consume
la API anterior (ver `DECISIONES.md` D-020). No está en el mismo despliegue que el
backend — corre localmente con Expo o se instala vía EAS, no en Render.

```bash
cd frontend
npm install
npx expo start
```

### Demos en vivo

```bash
python scripts/demo_en_vivo.py           # una parcela: recomendación y recálculo interactivo
python scripts/demo_programacion.py      # varios productores consolidados en vehículos (T-10)
python scripts/demo_programacion.py 10:00   # mismo plan con la ventana cerrando a las 10:00
python scripts/evaluar_modelos.py        # predictivo vs. determinista vs. ingenuo (T-14, D-003)
```

Guion completo de la demostración y relación con los objetivos: `docs/cumplimiento-objetivos.md`.
Arquitectura de los tres equipos: `docs/arquitectura.md`. Pruebas conjuntas: `docs/pruebas-integracion.md`.

---

## Estructura

```
CodeBack/
├─ app/
│  ├─ main.py                  # aplicación FastAPI — registra routers y dependencias
│  ├─ config.py                # settings y carga de config/parametros.yaml
│  ├─ db.py                    # engine y sesión
│  ├─ models/                  # SQLAlchemy (entidades.py)
│  ├─ schemas/                 # Pydantic — ingesta.py, planes.py, recomendacion.py
│  ├─ api/                     # routers
│  │  ├─ ingesta.py            #   recibe de equipos 1 y 3
│  │  ├─ planes.py             #   consulta del plan
│  │  ├─ insumos.py            #   consulta de insumos
│  │  └─ recomendacion.py      #   POST /api/v1/recomendar (Equipo 3, en vivo)
│  ├─ core/
│  │  ├─ proyeccion/           # cosecha esperada: base.py (determinista), predictivo.py, metricas.py
│  │  ├─ programacion/         # EL NÚCLEO: fechas.py, restricciones.py, heuristica.py
│  │  ├─ insumos/              # derivados del plan: estimacion.py, metricas.py
│  │  ├─ servicio.py           # orquesta proyección + programación + insumos
│  │  └─ seguridad.py          # verificación de token entre servicios (D-010/D-018)
│  └─ integracion/             # clientes equipos 1 y 3
├─ frontend/                   # app móvil Expo/React Native — único frontend (D-020)
├─ config/parametros.yaml      # tiempos, capacidades, coeficientes (NO en el código)
├─ data/                       # muestras y procedencia (pendiente de llenar, ver data/README.md)
├─ docs/                       # contrato v2, arquitectura, pruebas de integración, cumplimiento, evaluación
├─ migrations/                 # Alembic
├─ scripts/                    # demos de sustentación: demo_en_vivo, demo_programacion, evaluar_modelos
├─ render.yaml                 # despliegue del backend en Render (ver sección arriba)
└─ tests/
   └─ casos/                   # casos de cálculo con respuesta conocida
```

---

## Cómo trabajamos

1. Una rama por tarea: `T-10-heuristica-programacion`.
2. **Nadie hace merge de su propio PR.** La revisión la hace alguien **de la otra pareja**.
3. Toda decisión técnica que cambie el rumbo se anota en `DECISIONES.md` en el mismo PR.
4. Los parámetros del dominio van en `config/parametros.yaml`, nunca dentro del código.
5. Si una tarea se bloquea más de dos días, se lleva a la sesión de seguimiento.

---

## Stack

**Backend:** Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · pandas ·
scikit-learn · pytest · Docker · Render (despliegue)

**App móvil:** Expo · React Native — único frontend del proyecto (ver `DECISIONES.md` D-020)

Todas con licencias libres. El presupuesto de software del anteproyecto es $0 (planes free de Render).
