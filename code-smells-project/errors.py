"""Erros de domínio — traduzidos para HTTP pelo handler central.

Permitem que services e repositories sinalizem falhas sem conhecer o
protocolo de transporte (resolve ARCH-01 e QUAL-03).
"""


class DomainError(Exception):
    """Erro de negócio genérico."""

    status_code = 400

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ValidacaoError(DomainError):
    """Entrada inválida (formato, campos, faixas)."""

    status_code = 400


class NaoEncontradoError(DomainError):
    """Recurso inexistente."""

    status_code = 404

    def __init__(self, mensagem="Recurso não encontrado"):
        super().__init__(mensagem)


class ConflitoError(DomainError):
    """Conflito de estado (ex.: estoque insuficiente)."""

    status_code = 400


class NaoAutorizadoError(DomainError):
    """Credencial ausente ou inválida."""

    status_code = 401

    def __init__(self, mensagem="Não autorizado"):
        super().__init__(mensagem)


class ProibidoError(DomainError):
    """Autenticado, mas sem permissão para a operação."""

    status_code = 403
