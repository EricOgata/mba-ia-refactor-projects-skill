"""Error handling centralizado — traduz exceções em respostas JSON."""

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db
from errors import DomainError


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        db.session.rollback()
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        app.logger.exception('Erro não tratado: %s', error)
        return jsonify({'error': 'Erro interno'}), 500
