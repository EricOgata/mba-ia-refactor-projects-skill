"""Service de pedidos — regras de criação, status e notificações.

Resolve ARCH-01 (cálculo de total, validação de estoque e transições de
status saem do controller) e SEC-06 (notificações deixam de ser `print`
de PII e passam por um serviço dedicado).
"""

from config import Config
from errors import NaoEncontradoError, ValidacaoError
from models.produto import ItemPedido
from repositories import pedido_repository, produto_repository, usuario_repository
from services import notificacao_service


def listar():
    return pedido_repository.listar()


def listar_por_usuario(usuario_id):
    return pedido_repository.listar_por_usuario(usuario_id)


def criar(usuario_id, itens):
    if usuario_repository.buscar_por_id(usuario_id) is None:
        raise ValidacaoError("Usuário não encontrado")

    itens_validados = [
        ItemPedido.criar(item["produto_id"], item["quantidade"]) for item in itens
    ]

    _validar_produtos(itens_validados)

    resultado = pedido_repository.criar(
        usuario_id,
        [{"produto_id": i.produto_id, "quantidade": i.quantidade} for i in itens_validados],
    )

    notificacao_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return resultado


def _validar_produtos(itens):
    """Pré-valida produto inexistente como 400 (preserva contrato original)."""
    for item in itens:
        if produto_repository.buscar_por_id(item.produto_id) is None:
            raise ValidacaoError(f"Produto {item.produto_id} não encontrado")


def atualizar_status(pedido_id, novo_status):
    if novo_status not in Config.STATUS_PEDIDO_VALIDOS:
        raise ValidacaoError("Status inválido")

    if pedido_repository.buscar_por_id(pedido_id) is None:
        raise NaoEncontradoError("Pedido não encontrado")

    pedido_repository.atualizar_status(pedido_id, novo_status)

    if novo_status == "aprovado":
        notificacao_service.pedido_aprovado(pedido_id)
    elif novo_status == "cancelado":
        notificacao_service.pedido_cancelado(pedido_id)

    return True


def relatorio_vendas():
    resumo = pedido_repository.resumo_vendas()

    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def _calcular_desconto(faturamento):
    """Faixas de desconto vêm de `Config.FAIXAS_DESCONTO` (regra de negócio)."""
    for limite, percentual in Config.FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return 0
