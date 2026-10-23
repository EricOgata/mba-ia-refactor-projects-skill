"""Service de notificações — resolve SEC-06 (nada de PII em stdout).

Substitui os `print` de "ENVIANDO EMAIL/SMS/PUSH" que misturavam efeito
colateral, log e PII. Registra via `logging` apenas identificadores
técnicos, sem e-mail, senha ou dados pessoais.
"""

import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("notificacao.pedido_criado pedido_id=%s usuario_id=%s", pedido_id, usuario_id)


def pedido_aprovado(pedido_id):
    logger.info("notificacao.pedido_aprovado pedido_id=%s", pedido_id)


def pedido_cancelado(pedido_id):
    logger.info("notificacao.pedido_cancelado pedido_id=%s", pedido_id)
