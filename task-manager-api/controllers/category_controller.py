"""Controllers de categorias."""

from flask import jsonify

from controllers.common import json_body
from services.category_service import CategoryService


def list_categories():
    return jsonify(CategoryService().list_categories()), 200


def create_category():
    payload = json_body()
    return jsonify(CategoryService().create_category(payload)), 201


def update_category(category_id):
    payload = json_body()
    return jsonify(CategoryService().update_category(category_id, payload)), 200


def delete_category(category_id):
    CategoryService().delete_category(category_id)
    return jsonify({'message': 'Categoria deletada'}), 200
