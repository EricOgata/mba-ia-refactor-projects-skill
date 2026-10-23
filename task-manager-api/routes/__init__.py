"""Composição das rotas da aplicação."""

from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

BLUEPRINTS = (task_bp, user_bp, category_bp, report_bp)


def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
