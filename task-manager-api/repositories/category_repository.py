"""Acesso a dados de Category."""

from sqlalchemy import func

from database import db
from models.category import Category


class CategoryRepository:
    def get_all(self):
        return Category.query.order_by(Category.id).all()

    def get_by_id(self, category_id):
        return db.session.get(Category, category_id)

    def create(self, **fields):
        category = Category(**fields)
        db.session.add(category)
        db.session.commit()
        return category

    def save(self):
        db.session.commit()

    def delete(self, category):
        db.session.delete(category)
        db.session.commit()

    def count(self):
        return db.session.query(func.count(Category.id)).scalar()
