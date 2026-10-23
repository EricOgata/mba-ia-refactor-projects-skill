"""Repository de produtos — único ponto de acesso à tabela `produtos`.

Todas as queries são parametrizadas (resolve SEC-01). Sem HTTP, sem regra
de negócio: apenas persistência e mapeamento linha → dict.
"""

from database import get_db

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _to_dict(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar():
    cursor = get_db().cursor()
    cursor.execute(f"SELECT {_COLUNAS} FROM produtos")
    return [_to_dict(row) for row in cursor.fetchall()]


def buscar_por_id(produto_id):
    cursor = get_db().cursor()
    cursor.execute(f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,))
    return _to_dict(cursor.fetchone())


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    query = f"SELECT {_COLUNAS} FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor = get_db().cursor()
    cursor.execute(query, params)
    return [_to_dict(row) for row in cursor.fetchall()]


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()
    return cursor.rowcount > 0


def deletar(produto_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()
    return cursor.rowcount > 0


def baixar_estoque(produto_id, quantidade):
    """Débito condicional atômico — evita TOCTOU de estoque (QUAL-02b).

    Devolve True apenas se havia estoque suficiente no momento do UPDATE.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount > 0


def contar():
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    return cursor.fetchone()[0]
