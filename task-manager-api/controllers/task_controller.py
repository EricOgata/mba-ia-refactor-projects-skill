"""Controllers de tarefas: apenas orquestram request → service → response."""

from flask import jsonify, request

from controllers.common import json_body
from services.task_service import TaskService


def list_tasks():
    return jsonify(TaskService().list_tasks()), 200


def get_task(task_id):
    return jsonify(TaskService().get_task(task_id)), 200


def create_task():
    payload = json_body()
    return jsonify(TaskService().create_task(payload)), 201


def update_task(task_id):
    payload = json_body()
    return jsonify(TaskService().update_task(task_id, payload)), 200


def delete_task(task_id):
    TaskService().delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    return jsonify(TaskService().search_tasks(
        query=request.args.get('q'),
        status=request.args.get('status'),
        priority=request.args.get('priority'),
        user_id=request.args.get('user_id'),
    )), 200


def task_stats():
    return jsonify(TaskService().stats()), 200
