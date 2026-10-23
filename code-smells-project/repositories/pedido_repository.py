"""Repository de pedidos — acesso a `pedidos` e `itens_pedido`.

Resolve PERF-01: as listagens usam um único JOIN por relação para carregar
pedido + itens + nome do produto, em vez de N+1 queries aninhadas.
Débito de estoque é transacional e atômico (QUAL-02b).
"""

from database import get_db
from errors import ConflitoError, NaoEncontradoError

_LISTAGEM_SQL = """
    SELECT p.id            AS pedido_id,
           p.usuario_id    AS usuario_id,
           p.status        AS status,
           p.total         AS total,
           p.criado_em     AS criado_em,
           i.produto_id    AS produto_id,
           i.quantidade    AS quantidade,
           i.preco_unitario AS preco_unitario,
           pr.nome         AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr   ON pr.id = i.produto_id
"""


def _agrupar(rows):
    """Agrupa as linhas do JOIN em pedidos com lista de itens."""
    pedidos = {}
    for row in rows:
        pedido = pedidos.get(row["pedido_id"])
        if pedido is None:
            pedido = {
                "id": row["pedido_id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            pedidos[row["pedido_id"]] = pedido
        if row["produto_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def listar():
    cursor = get_db().cursor()
    cursor.execute(_LISTAGEM_SQL + " ORDER BY p.id")
    return _agrupar(cursor.fetchall())


def listar_por_usuario(usuario_id):
    cursor = get_db().cursor()
    cursor.execute(_LISTAGEM_SQL + " WHERE p.usuario_id = ? ORDER BY p.id", (usuario_id,))
    return _agrupar(cursor.fetchall())


def buscar_por_id(pedido_id):
    cursor = get_db().cursor()
    cursor.execute(_LISTAGEM_SQL + " WHERE p.id = ?", (pedido_id,))
    pedidos = _agrupar(cursor.fetchall())
    return pedidos[0] if pedidos else None


def criar(usuario_id, itens):
    """Cria pedido, valida estoque, grava itens e baixa estoque em transação única.

    `itens` é uma lista de dicts `{"produto_id": int, "quantidade": int}`.
    Levanta ConflitoError/NaoEncontradoError sem aplicar mudanças parciais.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")

        itens_normalizados = []
        total = 0.0

        for item in itens:
            produto_id = item["produto_id"]
            quantidade = item["quantidade"]

            cursor.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
                (produto_id,),
            )
            produto = cursor.fetchone()
            if produto is None:
                raise NaoEncontradoError(f"Produto {produto_id} não encontrado")

            if not baixar_estoque_cursor(cursor, produto_id, quantidade):
                raise ConflitoError(f"Estoque insuficiente para {produto['nome']}")

            total += produto["preco"] * quantidade
            itens_normalizados.append((produto_id, quantidade, produto["preco"]))

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        cursor.executemany(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            [(pedido_id, pid, qtd, preco) for pid, qtd, preco in itens_normalizados],
        )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def baixar_estoque_cursor(cursor, produto_id, quantidade):
    """Débito condicional — devolve False se o estoque não cobrir a quantidade."""
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount > 0


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return cursor.rowcount > 0


def resumo_vendas():
    """Agregações do relatório em uma única passada de leitura."""
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM pedidos")
    total_pedidos, faturamento = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'pendente'  THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'aprovado'  THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END)
        FROM pedidos
        """
    )
    pendentes, aprovados, cancelados = cursor.fetchone()
    return {
        "total_pedidos": total_pedidos,
        "faturamento": faturamento or 0,
        "pendentes": pendentes or 0,
        "aprovados": aprovados or 0,
        "cancelados": cancelados or 0,
    }


def contar():
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]
