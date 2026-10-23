"""Rotas de relatórios, operação e administração.

`POST /admin/query` foi removida: executava SQL arbitrário enviado pelo
cliente (SEC-01/SEC-04). A remoção é uma mudança de contrato deliberada e
está documentada em `reports/refactor-code-smells-project.md`.
"""

from flask import Blueprint, jsonify

import controllers
from config import Config
from middleware.auth import require_admin

relatorios_bp = Blueprint("relatorios", __name__)
relatorios_bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", controllers.relatorio_vendas, methods=["GET"])

operacao_bp = Blueprint("operacao", __name__)
operacao_bp.add_url_rule("/health", "health_check", controllers.health_check, methods=["GET"])


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": Config.APP_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@admin_bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    from services import admin_service

    admin_service.reset_database()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
