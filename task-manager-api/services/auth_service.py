"""Serviço de autenticação: emissão e validação de JWT."""

import jwt
from flask import current_app

from utils.helpers import utcnow


def create_access_token(user):
    now = utcnow()
    payload = {
        'sub': str(user.id),
        'role': user.role,
        'iat': now,
        'exp': now + _expiration(),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_access_token(token):
    return jwt.decode(
        token,
        current_app.config['SECRET_KEY'],
        algorithms=['HS256'],
    )


def _expiration():
    from datetime import timedelta

    seconds = current_app.config.get('JWT_EXPIRATION_SECONDS', 86400)
    return timedelta(seconds=seconds)
