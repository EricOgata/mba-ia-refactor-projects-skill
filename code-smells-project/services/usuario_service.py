"""Service de usuários e autenticação.

Resolve SEC-03: senhas passam a ser armazenadas e verificadas via hash com
salt (`werkzeug.security`), e o campo `senha` nunca é devolvido nas
respostas. Resolve ARCH-01: a verificação de credencial sai do controller.
"""

from werkzeug.security import check_password_hash, generate_password_hash

from errors import NaoAutorizadoError, NaoEncontradoError
from repositories import usuario_repository

_PREFIXOS_HASH = ("pbkdf2:", "scrypt:", "argon2")


def listar():
    return usuario_repository.listar()


def buscar_por_id(usuario_id):
    usuario = usuario_repository.buscar_por_id(usuario_id)
    if usuario is None:
        raise NaoEncontradoError("Usuário não encontrado")
    return usuario


def criar(dados):
    senha_hash = generate_password_hash(dados["senha"])
    usuario_id = usuario_repository.criar(dados["nome"], dados["email"], senha_hash)
    return {"id": usuario_id}


def autenticar(email, senha):
    usuario = usuario_repository.buscar_por_email(email)
    if usuario is None:
        raise NaoAutorizadoError("Email ou senha inválidos")

    stored = usuario["senha"] or ""
    if not _senha_confere(stored, senha):
        raise NaoAutorizadoError("Email ou senha inválidos")

    # upgrade transparente: hash legado/plaintext vira hash com salt
    if not stored.startswith(_PREFIXOS_HASH):
        usuario_repository.atualizar_senha(usuario["id"], generate_password_hash(senha))

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
    }


def _senha_confere(stored, senha_informada):
    """Aceita hash com salt e reconhece senhas legadas em texto puro."""
    if stored.startswith(_PREFIXOS_HASH):
        return check_password_hash(stored, senha_informada)
    return stored == senha_informada
