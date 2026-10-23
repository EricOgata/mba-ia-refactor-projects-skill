"""Rotas do recurso Usuários e autenticação."""

from flask import Blueprint

import controllers

usuarios_bp = Blueprint("usuarios", __name__)

usuarios_bp.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
usuarios_bp.add_url_rule("/usuarios/<int:id>", "buscar_usuario", controllers.buscar_usuario, methods=["GET"])
usuarios_bp.add_url_rule("/usuarios", "criar_usuario", controllers.criar_usuario, methods=["POST"])
usuarios_bp.add_url_rule("/login", "login", controllers.login, methods=["POST"])
