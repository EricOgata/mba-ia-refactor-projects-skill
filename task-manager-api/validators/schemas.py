"""Schemas de validação de entrada (marshmallow)."""

from marshmallow import EXCLUDE, Schema, ValidationError as MarshmallowValidationError
from marshmallow import fields, validate

from errors import ValidationError
from utils.helpers import COLOR_PATTERN, EMAIL_PATTERN, VALID_ROLES, VALID_STATUSES


class _BaseSchema(Schema):
    # Campos desconhecidos são ignorados, preservando o comportamento legado.
    class Meta:
        unknown = EXCLUDE


class TaskCreateSchema(_BaseSchema):
    title = fields.String(
        required=True,
        validate=validate.Length(
            min=3, max=200,
            error='Título deve ter entre 3 e 200 caracteres',
        ),
        error_messages={'required': 'Título é obrigatório'},
    )
    description = fields.String(load_default='', allow_none=True)
    status = fields.String(
        load_default='pending',
        validate=validate.OneOf(VALID_STATUSES, error='Status inválido'),
    )
    priority = fields.Integer(
        load_default=3,
        validate=validate.Range(min=1, max=5, error='Prioridade deve ser entre 1 e 5'),
    )
    user_id = fields.Integer(load_default=None, allow_none=True)
    category_id = fields.Integer(load_default=None, allow_none=True)
    due_date = fields.Date(load_default=None, allow_none=True)
    tags = fields.Raw(load_default=None, allow_none=True)


class TaskUpdateSchema(_BaseSchema):
    title = fields.String(
        validate=validate.Length(
            min=3, max=200,
            error='Título deve ter entre 3 e 200 caracteres',
        )
    )
    description = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(VALID_STATUSES, error='Status inválido'))
    priority = fields.Integer(
        validate=validate.Range(min=1, max=5, error='Prioridade deve ser entre 1 e 5')
    )
    user_id = fields.Integer(allow_none=True)
    category_id = fields.Integer(allow_none=True)
    due_date = fields.Date(allow_none=True)
    tags = fields.Raw(allow_none=True)


class UserCreateSchema(_BaseSchema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, error='Nome é obrigatório'),
        error_messages={'required': 'Nome é obrigatório'},
    )
    email = fields.String(
        required=True,
        validate=validate.Regexp(EMAIL_PATTERN, error='Email inválido'),
        error_messages={'required': 'Email é obrigatório'},
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=4, error='Senha deve ter no mínimo 4 caracteres'),
        error_messages={'required': 'Senha é obrigatória'},
    )
    role = fields.String(
        load_default='user',
        validate=validate.OneOf(VALID_ROLES, error='Role inválido'),
    )


class UserUpdateSchema(_BaseSchema):
    name = fields.String(validate=validate.Length(min=1, error='Nome é obrigatório'))
    email = fields.String(validate=validate.Regexp(EMAIL_PATTERN, error='Email inválido'))
    password = fields.String(validate=validate.Length(min=4, error='Senha muito curta'))
    role = fields.String(validate=validate.OneOf(VALID_ROLES, error='Role inválido'))
    active = fields.Boolean()


class LoginSchema(_BaseSchema):
    email = fields.String(required=True, error_messages={'required': 'Email e senha são obrigatórios'})
    password = fields.String(required=True, error_messages={'required': 'Email e senha são obrigatórios'})


class CategoryCreateSchema(_BaseSchema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, error='Nome é obrigatório'),
        error_messages={'required': 'Nome é obrigatório'},
    )
    description = fields.String(load_default='', allow_none=True)
    color = fields.String(
        load_default='#000000',
        validate=validate.Regexp(COLOR_PATTERN, error='Cor inválida. Use o formato #RRGGBB'),
    )


class CategoryUpdateSchema(_BaseSchema):
    name = fields.String(validate=validate.Length(min=1, error='Nome é obrigatório'))
    description = fields.String(allow_none=True)
    color = fields.String(validate=validate.Regexp(COLOR_PATTERN, error='Cor inválida. Use o formato #RRGGBB'))


def validate_schema(schema, payload):
    """Executa o schema e converte o primeiro erro em `ValidationError`."""
    try:
        return schema.load(payload or {})
    except MarshmallowValidationError as exc:
        for messages in exc.messages.values():
            if isinstance(messages, list) and messages:
                raise ValidationError(str(messages[0]))
            if isinstance(messages, str):
                raise ValidationError(messages)
            if isinstance(messages, dict) and messages:
                nested = next(iter(messages.values()))
                if isinstance(nested, list) and nested:
                    raise ValidationError(str(nested[0]))
        raise ValidationError('Dados inválidos')
