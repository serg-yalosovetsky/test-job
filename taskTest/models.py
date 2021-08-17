import uuid
from datetime import datetime

from slugify import slugify

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(250))
    currency = db.Column(db.String(3))
    
    def __repr__(self):
        return f'<Order {self.id} {self.price} {self.currency} {self.description}>'
