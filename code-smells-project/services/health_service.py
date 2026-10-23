"""Service de saúde da aplicação — contadores sem expor dados internos.

Resolve o vazamento de SEC-02 (`secret_key`) e QUAL-07 (`db_path`,
`debug` hardcoded) na resposta de `/health`.
"""

from config import Config
from repositories import pedido_repository, produto_repository, usuario_repository


def status():
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_repository.contar(),
            "usuarios": usuario_repository.contar(),
            "pedidos": pedido_repository.contar(),
        },
        "versao": Config.APP_VERSION,
        "ambiente": Config.ENVIRONMENT,
    }
