"""Registro de rotas, agrupadas por recurso (resolve Padrão 8)."""

from routes.pedido_routes import pedidos_bp
from routes.produto_routes import produtos_bp
from routes.relatorio_routes import admin_bp, operacao_bp, relatorios_bp
from routes.usuario_routes import usuarios_bp

BLUEPRINTS = (
    produtos_bp,
    usuarios_bp,
    pedidos_bp,
    relatorios_bp,
    operacao_bp,
    admin_bp,
)


def init_app(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
