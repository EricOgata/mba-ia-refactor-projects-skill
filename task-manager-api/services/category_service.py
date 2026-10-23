"""Regras de negócio do domínio de categorias."""

from errors import NotFoundError
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from validators.schemas import CategoryCreateSchema, CategoryUpdateSchema, validate_schema


class CategoryService:
    def __init__(self, category_repo=None, task_repo=None):
        self.categories = category_repo or CategoryRepository()
        self.tasks = task_repo or TaskRepository()

    def list_categories(self):
        counts = self.tasks.count_by_category()
        result = []
        for category in self.categories.get_all():
            data = category.to_dict()
            data['task_count'] = counts.get(category.id, 0)
            result.append(data)
        return result

    def create_category(self, payload):
        data = validate_schema(CategoryCreateSchema(), payload)
        category = self.categories.create(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#000000'),
        )
        return category.to_dict()

    def update_category(self, category_id, payload):
        category = self._get_or_404(category_id)
        data = validate_schema(CategoryUpdateSchema(), payload)
        for field in ('name', 'description', 'color'):
            if field in data:
                setattr(category, field, data[field])
        self.categories.save()
        return category.to_dict()

    def delete_category(self, category_id):
        category = self._get_or_404(category_id)
        self.categories.delete(category)

    def _get_or_404(self, category_id):
        category = self.categories.get_by_id(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        return category
