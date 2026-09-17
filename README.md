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
| **Front y plataforma** | David Arango Pineda · José Miguel Correa Sánchez | Datos y migraciones, API REST, contrato, integración, vistas Jinja2, Docker |

Detalle por persona y tarea en [`TAREAS.md`](TAREAS.md).

---

## Cómo levantarlo

Requisitos: Docker y Docker Compose.

```bash
git clone <url-del-repo>
cd platano-logistica
cp .env.example .env
docker compose up --build
```

La aplicación queda en http://localhost:8000
La documentación interactiva de la API, en http://localhost:8000/docs

### Migraciones

```bash
docker compose exec app alembic upgrade head
```

### Datos de muestra

```bash
docker compose exec app python -m app.seed
```

### Pruebas

```bash
docker compose exec app pytest
docker compose exec app pytest tests/casos -v   # casos de cálculo verificados a mano
```

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

## Estructura

```
platano-logistica/
├─ app/
│  ├─ main.py                  # aplicación FastAPI
│  ├─ config.py                # settings y carga de config/parametros.yaml
│  ├─ db.py                    # engine y sesión
│  ├─ models/                  # SQLAlchemy               → David
│  ├─ schemas/                 # Pydantic                 → José Miguel
│  ├─ api/                     # routers                  → José Miguel
│  │  ├─ ingesta.py            #   recibe de equipos 1 y 3
│  │  ├─ planes.py             #   consulta del plan
│  │  └─ insumos.py            #   consulta de insumos
│  ├─ core/
│  │  ├─ proyeccion/           # cosecha esperada         → Camilo   [backend]
│  │  │  ├─ base.py            #   determinista
│  │  │  ├─ predictivo.py      #   scikit-learn
│  │  │  └─ metricas.py
│  │  ├─ programacion/         # EL NÚCLEO                → Lizbeth  [backend]
│  │  │  ├─ fechas.py          #   fecha límite hacia atrás
│  │  │  ├─ restricciones.py   #   capacidad y ventana
│  │  │  └─ heuristica.py      #   los 4 pasos
│  │  └─ insumos/              # derivados del plan       → Lizbeth  [backend]
│  │     └─ estimacion.py
│  ├─ integracion/             # clientes equipos 1 y 3   → José M.  [front]
│  ├─ templates/               # vistas Jinja2            → David    [front]
│  └─ static/
├─ config/parametros.yaml      # tiempos, capacidades, coeficientes (NO en el código)
├─ data/                       # muestras y procedencia
├─ docs/                       # contrato, modelo de datos, OpenAPI exportado
├─ migrations/                 # Alembic
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

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Jinja2 · pandas · scikit-learn · pytest · Docker

Todas con licencias libres. El presupuesto de software del anteproyecto es $0.
