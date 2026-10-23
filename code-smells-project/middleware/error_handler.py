"""Tratamento de erro centralizado — resolve QUAL-03.

Substitui os 17 blocos `except Exception: return jsonify({"erro": str(e)})`
por um handler único que:
- traduz erros de domínio para o status correto;
- devolve 500 com mensagem genérica em falhas inesperadas;
- registra o detalhe apenas no log do servidor (sem vazar stack trace).
"""

import logging

from werkzeug.exceptions import HTTPException

from errors import DomainError

logger = logging.getLogger(__name__)

MENSAGEM_INTERNA = "Erro interno do servidor"


def init_app(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(erro):
        return {"erro": erro.mensagem, "sucesso": False}, erro.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(erro):
        return {"erro": erro.description, "sucesso": False}, erro.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(erro):
        logger.exception("erro inesperado na requisição")
        return {"erro": MENSAGEM_INTERNA, "sucesso": False}, 500
