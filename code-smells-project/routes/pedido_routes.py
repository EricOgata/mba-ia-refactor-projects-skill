"""Rotas do recurso Pedidos."""

from flask import Blueprint

import controllers

pedidos_bp = Blueprint("pedidos", __name__)

pedidos_bp.add_url_rule("/pedidos", "criar_pedido", controllers.criar_pedido, methods=["POST"])
pedidos_bp.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
pedidos_bp.add_url_rule(
    "/pedidos/usuario/<int:usuario_id>",
    "listar_pedidos_usuario",
    controllers.listar_pedidos_usuario,
    methods=["GET"],
)
pedidos_bp.add_url_rule(
    "/pedidos/<int:pedido_id>/status",
    "atualizar_status_pedido",
    controllers.atualizar_status_pedido,
    methods=["PUT"],
)
