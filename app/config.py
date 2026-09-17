"""Configuración y carga de los parámetros del dominio.

Los parámetros del dominio (tiempos de acarreo, capacidades, coeficientes de consumo)
NO viven aquí ni en el código: viven en config/parametros.yaml. Ver D-004 en DECISIONES.md.

Responsable: David — frente front y plataforma (T-03).  Los valores los levanta Lizbeth (T-05).
"""
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://platano:platano@db:5432/platano"
    app_env: str = "dev"
    log_level: str = "INFO"
    parametros_path: str = "config/parametros.yaml"

    class Config:
        env_file = ".env"


@lru_cache
def settings() -> Settings:
    return Settings()


@lru_cache
def parametros() -> dict:
    """Parámetros del dominio, cargados desde YAML."""
    ruta = Path(settings().parametros_path)
    with ruta.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
