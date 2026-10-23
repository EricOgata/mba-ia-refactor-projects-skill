"""Acesso a dados de User."""

from sqlalchemy import func

from database import db
from models.task import Task
from models.user import User


class UserRepository:
    def get_all(self):
        return User.query.order_by(User.id).all()

    def get_all_with_task_counts(self):
        return (
            db.session.query(User, func.count(Task.id))
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id)
            .order_by(User.id)
            .all()
        )

    def get_by_id(self, user_id):
        return db.session.get(User, user_id)

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def add(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def save(self):
        db.session.commit()

    def delete_with_tasks(self, user):
        Task.query.filter_by(user_id=user.id).delete(synchronize_session=False)
        db.session.delete(user)
        db.session.commit()

    def count(self):
        return db.session.query(func.count(User.id)).scalar()
