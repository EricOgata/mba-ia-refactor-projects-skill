"""Guarda de autenticação administrativa — resolve SEC-04.

As rotas administrativas passam a exigir um token de admin. O token vem de
ambiente (`ADMIN_TOKEN`); sem ele, as rotas administrativas falham fechado
(403) em vez de ficarem abertas. Sem `Authorization: Bearer <token>`
válido, responde 401.
"""

import hmac
import os
from functools import wraps

from errors import NaoAutorizadoError, ProibidoError


def _admin_token():
    return os.getenv("ADMIN_TOKEN")


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request

        esperado = _admin_token()
        if not esperado:
            raise ProibidoError("Autenticação administrativa não configurada")

        cabecalho = request.headers.get("Authorization", "")
        prefixo = "Bearer "
        if not cabecalho.startswith(prefixo):
            raise NaoAutorizadoError("Token administrativo ausente")

        token = cabecalho[len(prefixo):]
        if not hmac.compare_digest(token, esperado):
            raise NaoAutorizadoError("Token administrativo inválido")

        return func(*args, **kwargs)

    return wrapper
