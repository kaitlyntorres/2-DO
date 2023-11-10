from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

#This application has a bunch of URLs defined here so that we can have our views defined in several files and not a single one
#This is what Blueprints allows us to do
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() #This is for looking for a specific field in the SQL Table you sepcified
        if user:
            if check_password_hash(user.password, password): #Check if password is correct for the specified email in the User table
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
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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

""" 
#Creating Database Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True) #ID will be incremented on its own
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Foreign key is the user.id that created the note
    title = db.Column(db.String(1000)) #This will be the title of the task that was created
    description = db.Column(db.String(10000)) #The user can add notes and detail to tasks that they are creating
    due_time = db.Column(db.Time) # HH:MM:SS.ssss format
    due_date = db.Column(db.Date) # YYYY-MM-DD Format
    tag = db.Column(db.String(6)) 
    priority = db.Column(db.String(6)) #should only be 'low', 'medium', 'high'

 """