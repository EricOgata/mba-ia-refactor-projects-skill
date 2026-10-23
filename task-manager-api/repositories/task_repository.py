"""Acesso a dados de Task. Único ponto de queries do domínio de tarefas."""

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from utils.helpers import VALID_STATUSES


class TaskRepository:
    def get_all(self):
        return (
            Task.query
            .options(joinedload(Task.user), joinedload(Task.category))
            .order_by(Task.id)
            .all()
        )

    def get_by_id(self, task_id):
        return db.session.get(Task, task_id)

    def get_by_user(self, user_id):
        return Task.query.filter_by(user_id=user_id).order_by(Task.id).all()

    def search(self, query=None, status=None, priority=None, user_id=None):
        tasks = Task.query
        if query:
            # `.contains()` gera parâmetro vinculado (sem interpolação de SQL).
            tasks = tasks.filter(or_(Task.title.contains(query), Task.description.contains(query)))
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority is not None:
            tasks = tasks.filter(Task.priority == priority)
        if user_id is not None:
            tasks = tasks.filter(Task.user_id == user_id)
        return tasks.order_by(Task.id).all()

    def create(self, **fields):
        task = Task(**fields)
        db.session.add(task)
        db.session.commit()
        return task

    def save(self):
        db.session.commit()

    def delete(self, task):
        db.session.delete(task)
        db.session.commit()

    def delete_by_user(self, user_id):
        Task.query.filter_by(user_id=user_id).delete(synchronize_session=False)

    def count(self):
        return db.session.query(func.count(Task.id)).scalar()

    def count_by_status(self):
        rows = (
            db.session.query(Task.status, func.count(Task.id))
            .group_by(Task.status)
            .all()
        )
        counts = {status: 0 for status in VALID_STATUSES}
        counts.update({status: total for status, total in rows})
        return counts

    def count_by_priority(self):
        rows = (
            db.session.query(Task.priority, func.count(Task.id))
            .group_by(Task.priority)
            .all()
        )
        return {priority: total for priority, total in rows}

    def count_by_category(self):
        rows = (
            db.session.query(Task.category_id, func.count(Task.id))
            .filter(Task.category_id.isnot(None))
            .group_by(Task.category_id)
            .all()
        )
        return {category_id: total for category_id, total in rows}

    def count_created_since(self, since):
        return (
            db.session.query(func.count(Task.id))
            .filter(Task.created_at >= since)
            .scalar()
        )

    def count_completed_since(self, since):
        return (
            db.session.query(func.count(Task.id))
            .filter(Task.status == 'done', Task.updated_at >= since)
            .scalar()
        )

    def get_overdue(self, now):
        return (
            Task.query
            .filter(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status.notin_(['done', 'cancelled']),
            )
            .order_by(Task.id)
            .all()
        )

    def productivity_by_user(self):
        """Retorna (total_por_usuario, concluidas_por_usuario) em 2 queries."""
        totals = dict(
            db.session.query(Task.user_id, func.count(Task.id))
            .filter(Task.user_id.isnot(None))
            .group_by(Task.user_id)
            .all()
        )
        completed = dict(
            db.session.query(Task.user_id, func.count(Task.id))
            .filter(Task.user_id.isnot(None), Task.status == 'done')
            .group_by(Task.user_id)
            .all()
        )
        return totals, completed
