"""Service administrativo — resolve ARCH-02 (SQL saiu do entrypoint)."""

from database import get_db

_TABELAS = ("itens_pedido", "pedidos", "produtos", "usuarios")


def reset_database():
    """Limpa as tabelas na ordem correta de dependência (sem re-seed)."""
    db = get_db()
    cursor = db.cursor()
    for tabela in _TABELAS:
        cursor.execute(f"DELETE FROM {tabela}")  # noqa: S608 — nomes fixos da lista acima
    db.commit()
    return True
