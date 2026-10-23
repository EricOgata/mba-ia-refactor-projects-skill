"""Schemas de validação de entrada — formato e tipos (resolve QUAL-02).

Validação de *schema* fica aqui e é chamada pelo controller; validação de
*regra de negócio* (ex.: estoque) fica nos services. Devolvem estruturas
simples ou levantam `ValidacaoError`.
"""

from errors import ValidacaoError

CATEGORIA_MAX = 100
EMAIL_MAX = 254


def _exigir_json(dados):
    if not isinstance(dados, dict):
        raise ValidacaoError("Dados inválidos")
    return dados


def _numero(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacaoError(f"{campo} deve ser numérico")
    return valor


def _inteiro(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidacaoError(f"{campo} deve ser um inteiro")
    return valor


def produto(dados):
    dados = _exigir_json(dados)
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidacaoError(
                {"nome": "Nome é obrigatório", "preco": "Preço é obrigatório", "estoque": "Estoque é obrigatório"}[campo]
            )

    preco = _numero(dados["preco"], "preco")
    estoque = _inteiro(dados["estoque"], "estoque")
    categoria = dados.get("categoria", "geral")
    if not isinstance(categoria, str):
        raise ValidacaoError("categoria deve ser texto")
    if len(categoria) > CATEGORIA_MAX:
        raise ValidacaoError("categoria muito longa")

    return {
        "nome": dados["nome"],
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria or "geral",
    }


def usuario(dados):
    dados = _exigir_json(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidacaoError("Nome, email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (nome, email, senha)):
        raise ValidacaoError("Nome, email e senha devem ser texto")
    if len(email) > EMAIL_MAX:
        raise ValidacaoError("email muito longo")

    return {"nome": nome, "email": email, "senha": senha}


def login(dados):
    dados = _exigir_json(dados)
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ValidacaoError("Email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (email, senha)):
        raise ValidacaoError("Email e senha devem ser texto")

    return {"email": email, "senha": senha}


def pedido(dados):
    dados = _exigir_json(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidacaoError("Usuario ID é obrigatório")
    _inteiro(usuario_id, "usuario_id")
    if not isinstance(itens, list) or len(itens) == 0:
        raise ValidacaoError("Pedido deve ter pelo menos 1 item")

    for item in itens:
        if not isinstance(item, dict) or "produto_id" not in item or "quantidade" not in item:
            raise ValidacaoError("Cada item deve ter produto_id e quantidade")
        _inteiro(item["produto_id"], "produto_id")
        _inteiro(item["quantidade"], "quantidade")

    return {"usuario_id": usuario_id, "itens": itens}


def status_pedido(dados, status_validos):
    dados = _exigir_json(dados)
    novo_status = dados.get("status", "")
    if novo_status not in status_validos:
        raise ValidacaoError("Status inválido")
    return novo_status
