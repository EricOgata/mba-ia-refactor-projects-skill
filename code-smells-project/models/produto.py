"""Modelos de domínio — invariantes de entidade, sem SQL e sem HTTP.

Recebem dados já desserializados e devolvem objetos imutáveis ou levantam
erros de domínio. As regras de faixa/lista vêm de `config.Config`.
"""

from dataclasses import dataclass

from config import Config
from errors import ValidacaoError


@dataclass(frozen=True)
class Produto:
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str

    @classmethod
    def criar(cls, nome, descricao, preco, estoque, categoria=None):
        nome = (nome or "").strip()
        categoria = categoria or "geral"

        if len(nome) < Config.NOME_PRODUTO_MIN:
            raise ValidacaoError("Nome muito curto")
        if len(nome) > Config.NOME_PRODUTO_MAX:
            raise ValidacaoError("Nome muito longo")
        if preco < 0:
            raise ValidacaoError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValidacaoError("Estoque não pode ser negativo")
        if categoria not in Config.CATEGORIAS_VALIDAS:
            raise ValidacaoError(
                "Categoria inválida. Válidas: " + str(list(Config.CATEGORIAS_VALIDAS))
            )

        return cls(nome=nome, descricao=descricao or "", preco=preco, estoque=int(estoque), categoria=categoria)


@dataclass(frozen=True)
class ItemPedido:
    produto_id: int
    quantidade: int

    @classmethod
    def criar(cls, produto_id, quantidade):
        if not isinstance(produto_id, int) or isinstance(produto_id, bool):
            raise ValidacaoError("produto_id deve ser um inteiro")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValidacaoError("quantidade deve ser um inteiro maior que zero")
        return cls(produto_id=produto_id, quantidade=quantidade)
