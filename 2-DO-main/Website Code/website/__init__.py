"""
Flask Web Application Configuration

This module defines a Flask web application with configuration for a SQLite database using Flask-SQLAlchemy
and user authentication using Flask-Login.

Modules:
    - Flask: Micro web framework for Python.
    - SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
    - os: Operating system module for interacting with the operating system.
    - flask_login: User session management for Flask.

Classes:
    - db: SQLAlchemy object for database interaction.
    - LoginManager: Manages user authentication for the application.

Constants:
    - DB_NAME (str): Name of the SQLite database file.

Functions:
    - create_app: Factory function to create and configure the Flask application.

Usage:
    Create the Flask application by calling the create_app function.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Database object
db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app(database_uri="sqlite:///" + DB_NAME):
    """
    Create and configure the Flask application.

    Args:
        database_uri (str, optional): URI for the SQLite database. Defaults to "sqlite:///database.db".

    Returns:
        Flask: Configured Flask application.
    """

    app = Flask(__name__)
    
    # Set Flask configuration options
    app.config['SECRET_KEY'] = 'THIS IS THE KEY FOR THE APP'  # Can be anything you want but you want to hide this
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri  # Telling Flask where the database is located

    # Initialize the SQLAlchemy database
    db.init_app(app)

    # Import views and authentication blueprints
    from .views import views
    from .auth import auth

    # Register blueprints with the application
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import User and Task models
    from .models import User, Task

    # Uncomment the line below if the database needs to be created for the first time
    # create_database(app)  # This is for the first-time creation of the database

    # Create all tables in the database
    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """
        Load a user from the database using the user ID.

        Args:
            id (int): User ID.

        Returns:
            User: User object.
        """
        return User.query.get(int(id))

    return app
