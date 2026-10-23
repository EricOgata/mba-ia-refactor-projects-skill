"""Registro de rotas de categorias."""

from flask import Blueprint

from controllers import category_controller as controller

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', view_func=controller.list_categories, methods=['GET'])
category_bp.add_url_rule('/categories', view_func=controller.create_category, methods=['POST'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=controller.update_category, methods=['PUT'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=controller.delete_category, methods=['DELETE'])
