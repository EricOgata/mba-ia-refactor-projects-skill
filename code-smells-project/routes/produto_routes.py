"""Rotas do recurso Produtos — apenas registro URL → handler."""

from flask import Blueprint

import controllers

produtos_bp = Blueprint("produtos", __name__)

produtos_bp.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])
produtos_bp.add_url_rule("/produtos/busca", "buscar_produtos", controllers.buscar_produtos, methods=["GET"])
produtos_bp.add_url_rule("/produtos/<int:id>", "buscar_produto", controllers.buscar_produto, methods=["GET"])
produtos_bp.add_url_rule("/produtos", "criar_produto", controllers.criar_produto, methods=["POST"])
produtos_bp.add_url_rule("/produtos/<int:id>", "atualizar_produto", controllers.atualizar_produto, methods=["PUT"])
produtos_bp.add_url_rule("/produtos/<int:id>", "deletar_produto", controllers.deletar_produto, methods=["DELETE"])
