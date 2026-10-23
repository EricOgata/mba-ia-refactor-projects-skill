import hashlib

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.helpers import utcnow


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        # Nunca serializar `password` (hash) em respostas da API.
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        """Valida a senha; aceita hashes MD5 legados e os migra no login."""
        if self._is_legacy_md5(self.password):
            if self.password == hashlib.md5(pwd.encode()).hexdigest():
                self.set_password(pwd)
                return True
            return False
        return check_password_hash(self.password, pwd)

    @staticmethod
    def _is_legacy_md5(value):
        if not value or len(value) != 32:
            return False
        return all(c in '0123456789abcdef' for c in value.lower())

    def is_admin(self):
        return self.role == 'admin'
