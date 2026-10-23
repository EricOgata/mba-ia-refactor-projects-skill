"""Composition root: cria a aplicação, inicializa recursos e registra rotas."""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from config.settings import Config
from database import db
from middleware.auth import init_auth
from middleware.error_handler import register_error_handlers
from routes import register_blueprints
from utils.helpers import utcnow

migrate = Migrate()


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)
    register_error_handlers(app)
    init_auth(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(utcnow())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    return app


app = create_app()


if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT'],
    )
