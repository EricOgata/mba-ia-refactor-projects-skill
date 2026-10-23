"""Exceções de domínio.

Services e controllers lançam estas exceções; o error handler central
(`middleware/error_handler.py`) traduz cada uma em status HTTP e corpo JSON.
"""


class DomainError(Exception):
    """Erro de domínio com status HTTP associado."""

    status_code = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    status_code = 400


class UnauthorizedError(DomainError):
    status_code = 401


class ForbiddenError(DomainError):
    status_code = 403


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409
