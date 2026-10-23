"""Service de produtos — regras do catálogo (resolve ARCH-01/ARCH-03).

Não conhece HTTP: recebe dados já validados (schema) e devolve estruturas
simples. Regras de entidade ficam em `models.produto.Produto`.
"""

from errors import NaoEncontradoError
from models.produto import Produto
from repositories import produto_repository


def listar():
    return produto_repository.listar()


def buscar_por_id(produto_id):
    produto = produto_repository.buscar_por_id(produto_id)
    if produto is None:
        raise NaoEncontradoError("Produto não encontrado")
    return produto


def criar(dados):
    produto = Produto.criar(
        nome=dados["nome"],
        descricao=dados["descricao"],
        preco=dados["preco"],
        estoque=dados["estoque"],
        categoria=dados["categoria"],
    )
    produto_id = produto_repository.criar(
        produto.nome, produto.descricao, produto.preco, produto.estoque, produto.categoria
    )
    return {"id": produto_id}


def atualizar(produto_id, dados):
    if produto_repository.buscar_por_id(produto_id) is None:
        raise NaoEncontradoError("Produto não encontrado")

    produto = Produto.criar(
        nome=dados["nome"],
        descricao=dados["descricao"],
        preco=dados["preco"],
        estoque=dados["estoque"],
        categoria=dados["categoria"],
    )
    produto_repository.atualizar(
        produto_id, produto.nome, produto.descricao, produto.preco, produto.estoque, produto.categoria
    )
    return True


def deletar(produto_id):
    if produto_repository.buscar_por_id(produto_id) is None:
        raise NaoEncontradoError("Produto não encontrado")
    produto_repository.deletar(produto_id)
    return True


def buscar(termo, categoria, preco_min, preco_max):
    resultados = produto_repository.buscar(termo, categoria, preco_min, preco_max)
    return resultados, len(resultados)
