"""Regras de negócio do domínio de usuários e login."""

from errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from models.user import User
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.auth_service import create_access_token
from validators.schemas import LoginSchema, UserCreateSchema, UserUpdateSchema, validate_schema


class UserService:
    def __init__(self, user_repo=None, task_repo=None):
        self.users = user_repo or UserRepository()
        self.tasks = task_repo or TaskRepository()

    def list_users(self):
        result = []
        for user, task_count in self.users.get_all_with_task_counts():
            data = user.to_dict()
            data['task_count'] = task_count
            result.append(data)
        return result

    def get_user(self, user_id):
        user = self._get_or_404(user_id)
        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in self.tasks.get_by_user(user_id)]
        return data

    def get_user_tasks(self, user_id):
        self._get_or_404(user_id)
        result = []
        for task in self.tasks.get_by_user(user_id):
            result.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'created_at': str(task.created_at),
                'due_date': str(task.due_date) if task.due_date else None,
                'overdue': task.is_overdue(),
            })
        return result

    def create_user(self, payload):
        data = validate_schema(UserCreateSchema(), payload)
        if self.users.get_by_email(data['email']):
            raise ConflictError('Email já cadastrado')

        user = User(name=data['name'], email=data['email'], role=data['role'])
        user.set_password(data['password'])
        self.users.add(user)
        return user.to_dict()

    def update_user(self, user_id, payload):
        user = self._get_or_404(user_id)
        data = validate_schema(UserUpdateSchema(), payload)

        if 'email' in data:
            existing = self.users.get_by_email(data['email'])
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        for field in ('name', 'role', 'active'):
            if field in data:
                setattr(user, field, data[field])

        self.users.save()
        return user.to_dict()

    def delete_user(self, user_id):
        user = self._get_or_404(user_id)
        self.users.delete_with_tasks(user)

    def login(self, payload):
        data = validate_schema(LoginSchema(), payload)
        user = self.users.get_by_email(data['email'])
        if not user or not user.check_password(data['password']):
            raise UnauthorizedError('Credenciais inválidas')
        if not user.active:
            raise ForbiddenError('Usuário inativo')

        # `check_password` pode ter re-hasheado uma senha MD5 legada.
        self.users.save()
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': create_access_token(user),
        }

    def _get_or_404(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user
