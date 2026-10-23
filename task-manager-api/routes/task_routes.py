"""Registro de rotas de tarefas (somente mapeamento URL → controller)."""

from flask import Blueprint

from controllers import task_controller as controller

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', view_func=controller.list_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks', view_func=controller.create_task, methods=['POST'])
task_bp.add_url_rule('/tasks/search', view_func=controller.search_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', view_func=controller.task_stats, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=controller.get_task, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=controller.update_task, methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=controller.delete_task, methods=['DELETE'])
