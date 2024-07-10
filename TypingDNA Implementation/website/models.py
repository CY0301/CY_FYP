from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    typing_id = db.Column(db.String(100), default=str(uuid.uuid4()))
    secret_key = db.Column(db.String(32), unique=True, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    upload_date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('files', lazy=True))
