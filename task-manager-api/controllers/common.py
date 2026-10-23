"""Helpers compartilhados pelos controllers."""

from flask import request

from errors import ValidationError


def json_body():
    """Retorna o corpo JSON como dict ou lança `ValidationError` (400)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError('Dados inválidos')
    return data
