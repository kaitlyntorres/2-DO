"""
Authentication Blueprint

This module defines routes and functions related to user authentication using the Flask Blueprint 'auth'.

Modules:
    - Flask: Micro web framework for Python.
    - Blueprint: Organize a group of related views and other code.
    - render_template: Render HTML templates.
    - request: Handle incoming HTTP requests.
    - flash: Provide feedback messages to the user.
    - redirect: Redirect to a different endpoint.
    - url_for: Generate URLs for Flask views.
    - User: User model for database interaction.
    - generate_password_hash, check_password_hash: Secure password hashing.
    - db: SQLAlchemy object for database interaction.
    - login_user, login_required, logout_user, current_user: User authentication functionality.

Functions:
    - login: Route for user login. Handles both GET and POST requests.
    - logout: Route for user logout. Requires user to be logged in.
    - sign_up: Route for user registration. Handles both GET and POST requests.

Usage:
    Define the 'auth' Blueprint and use it to define authentication-related routes and functions.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

# This application has a bunch of URLs defined here so that we can have our views defined in several files and not a single one
# This is what Blueprints allows us to do
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    GET: Render the login page.
    POST: Verify user credentials and log in if valid.

    Returns:
        GET: Rendered login page.
        POST: Redirect to the home page on successful login, or render login page with error messages.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()  # This is for looking for a specific field in the SQL Table you specified
        if user:
            if check_password_hash(user.password, password):  # Check if the password is correct for the specified email in the User table
                flash('Logged in Successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect Password", category='error')
        else:
            flash("Email does not exist.", category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    """
    Handle user logout. Requires the user to be logged in.

    Returns:
        Redirect to the login page.
    """
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Handle user registration.

    GET: Render the sign-up page.
    POST: Validate user input, create a new user account, and redirect to the home page on success.

    Returns:
        GET: Rendered sign-up page.
        POST: Redirect to the home page on successful registration or render the sign-up page with error messages.
    """
    if request.method == "POST":
        email = request.form.get('email')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists", category='error')
        elif len(email) < 4:
            flash('Email must be longer than 4 characters.', category='error')
        elif len(firstname) < 2:
            flash('First Name must be longer than 1 character.', category='error')
        elif len(lastname) < 2:
            flash('Last Name must be longer than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=firstname, last_name=lastname, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account Successfully Created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)