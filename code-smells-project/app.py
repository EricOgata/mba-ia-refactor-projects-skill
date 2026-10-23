"""Entrypoint — apenas composição da aplicação.

Cria o app, carrega config de ambiente, registra middlewares, persistência
e rotas. Nenhuma regra de negócio, SQL ou segredo literal aqui
(resolve QUAL-07, SEC-02, ARCH-02).
"""

import logging

from flask import Flask
from flask_cors import CORS

import database
import routes
from config import Config, require_secret_key
from middleware import error_handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    CORS(app)

    database.init_app(app)
    error_handler.init_app(app)
    routes.init_app(app)

    return app


app = create_app()


if __name__ == "__main__":
    require_secret_key(app)
    with app.app_context():
        database.get_db()

    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{Config.PORT}")
    print("=" * 50)

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
