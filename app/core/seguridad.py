"""Verificación del token compartido entre servicios (D-010).

El token se activa solo si la variable de entorno INTEGRACION_TOKEN está
configurada. Sin ella, la dependencia no bloquea nada — así el cambio se puede
desplegar sin romper la integración ya en marcha con los equipos 1 y 3, y el
token se activa después, coordinando el momento con ellos.

Responsable: José Miguel — frente front y plataforma (T-11, T-12)
"""
import os

from fastapi import Header, HTTPException, status


def verificar_token_integracion(authorization: str | None = Header(default=None)) -> None:
    token_esperado = os.environ.get("INTEGRACION_TOKEN")
    if not token_esperado:
        return
    if authorization != f"Bearer {token_esperado}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de integración inválido o ausente. Use 'Authorization: Bearer <token>' (D-010).",
        )
