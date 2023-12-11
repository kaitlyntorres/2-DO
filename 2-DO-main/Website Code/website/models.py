"""
Database Models for Flask Application

This module defines the database models for the Flask application using SQLAlchemy.

Modules:
    - db: SQLAlchemy object for database interaction.
    - UserMixin: Helper class for user authentication with Flask-Login.
    - func: SQL functions from SQLAlchemy.

Classes:
    - Task: Database model for tasks.
    - User: Database model for users, extends UserMixin for Flask-Login.

Attributes (Task):
    - id (int): Primary key for the task.
    - user_id (int): Foreign key referencing the user who created the task.
    - title (str): Title of the task.
    - description (str): Description or notes for the task.
    - due_date (str): Due date in YYYY-MM-DD format.
    - tag (str): Task tag.
    - priority (str): Task priority ('Low', 'Medium', 'High').
    - status (bool): Task status (False for incomplete, True for complete).
    - reminder_time (str): Reminder time.

Attributes (User):
    - id (int): Primary key for the user.
    - email (str): User email (unique).
    - password (str): User password.
    - first_name (str): User first name.
    - last_name (str): User last name.
    - tasks (relationship): One-to-Many relationship with Task.

Usage:
    Import this module in the Flask application to define the database models.
"""

from . import db  # imports from the website our db object
from flask_login import UserMixin  # Helps logs users in
from sqlalchemy.sql import func

class Task(db.Model):
    """
    Database model for tasks.

    Attributes:
        id (int): Primary key for the task.
        user_id (int): Foreign key referencing the user who created the task.
        title (str): Title of the task.
        description (str): Description or notes for the task.
        due_date (str): Due date in YYYY-MM-DD format.
        tag (str): Task tag.
        priority (str): Task priority ('Low', 'Medium', 'High').
        status (bool): Task status (False for incomplete, True for complete).
        reminder_time (str): Reminder time.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(1000))
    description = db.Column(db.String(10000))
    due_date = db.Column(db.String(40))
    tag = db.Column(db.String(6))
    priority = db.Column(db.String(6))
    status = db.Column(db.Boolean, default=False)
    reminder_time = db.Column(db.String(40))

class User(db.Model, UserMixin):
    """
    Database model for users.

    Attributes:
        id (int): Primary key for the user.
        email (str): User email (unique).
        password (str): User password.
        first_name (str): User first name.
        last_name (str): User last name.
        tasks (relationship): One-to-Many relationship with Task.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    tasks = db.relationship('Task')  
