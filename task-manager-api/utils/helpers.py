"""Funções utilitárias genéricas, sem estado e sem dependência de framework."""

import re
from datetime import datetime, timezone

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']

EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
COLOR_PATTERN = r'^#[0-9a-fA-F]{6}$'


def utcnow():
    """UTC atual como datetime naive.

    Substitui `datetime.utcnow()` (deprecated no Python 3.12) mantendo o
    mesmo tipo armazenado pelas colunas `DateTime` do banco.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(email) and re.match(EMAIL_PATTERN, email) is not None
