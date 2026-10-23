"""Middleware de autenticação JWT.

`AUTH_REQUIRED=false` (default) preserva o contrato original do projeto legado.
Com `AUTH_REQUIRED=true`, toda rota de escrita exige `Authorization: Bearer <token>`.
"""

import jwt
from flask import current_app, g, request

from errors import UnauthorizedError
from services.auth_service import decode_access_token

SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}
EXEMPT_PATHS = {'/login'}


def init_auth(app):
    @app.before_request
    def enforce_authentication():
        if not current_app.config.get('AUTH_REQUIRED'):
            return None
        if request.method in SAFE_METHODS or request.path in EXEMPT_PATHS:
            return None

        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            raise UnauthorizedError('Autenticação necessária')

        token = header[len('Bearer '):].strip()
        try:
            payload = decode_access_token(token)
        except jwt.PyJWTError:
            raise UnauthorizedError('Token inválido ou expirado')

        g.user_id = payload.get('sub')
        g.user_role = payload.get('role')
        return None
