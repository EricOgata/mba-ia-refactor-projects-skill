"""Controllers de usuários e login."""

from flask import jsonify

from controllers.common import json_body
from services.user_service import UserService


def list_users():
    return jsonify(UserService().list_users()), 200


def get_user(user_id):
    return jsonify(UserService().get_user(user_id)), 200


def create_user():
    payload = json_body()
    return jsonify(UserService().create_user(payload)), 201


def update_user(user_id):
    payload = json_body()
    return jsonify(UserService().update_user(user_id, payload)), 200


def delete_user(user_id):
    UserService().delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    return jsonify(UserService().get_user_tasks(user_id)), 200


def login():
    payload = json_body()
    return jsonify(UserService().login(payload)), 200
