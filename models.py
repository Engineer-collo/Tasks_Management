from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=date.today)

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        return email

    def set_password(self, password):
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationships
    profile = db.relationship('Profile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    todos = db.relationship('Todo', back_populates='user', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "date_created": self.date_created.isoformat()
        }

    def __repr__(self):
        return f"<User {self.email}>"

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    bio = db.Column(db.String(300))
    profile_picture_url = db.Column(db.String(300))
    date_created = db.Column(db.Date, nullable=False, default=date.today)

    @validates('username', 'bio')
    def validate_fields(self, key, value):
        if key == 'username':
            if len(value) < 3:
                raise ValueError("Username must be at least 3 characters long")
        elif key == 'bio':
            if len(value) < 10:
                raise ValueError("Bio must be at least 10 characters long")
        return value



    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship back to User
    user = db.relationship('User', back_populates='profile')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
            "date_created": self.date_created.isoformat(),
            "user_id": self.user_id
        }

    def __repr__(self):
        return f"<Profile {self.username}>"

class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=date.today)

    @validates('content')
    def validate_content(self, key, content):
        if len(content) < 10:
            raise ValueError("Content must be at least 10 characters long")
        return content

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship back to User
    user = db.relationship('User', back_populates='todos')

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "date_created": self.date_created.isoformat(),
            "user_id": self.user_id
        }

    def __repr__(self):
        return f"<Todo {self.content} | User {self.user_id}>"
