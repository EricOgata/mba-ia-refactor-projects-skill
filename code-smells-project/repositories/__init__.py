"""Repositories — único ponto de acesso a dados (resolve ARCH-02)."""

from repositories import pedido_repository, produto_repository, usuario_repository

__all__ = ["produto_repository", "usuario_repository", "pedido_repository"]
