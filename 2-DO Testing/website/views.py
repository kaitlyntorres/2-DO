from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Task
from . import db
import json
import jsonify

#This application has a bunch of URLs defined here so that we can have our views defined in several files and not a single one
#This is what Blueprints allows us to do
views = Blueprint('views', __name__)


## NEEDS TO BE PORTED OVER
#Decorator, calles on the function when this route is hit
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    #Find a way to query only the tasks that the user owns to show
    tasks = Task.query.all()

    # NEED TO IMPLEMENT THIS SECTION

    return render_template("home.html", user=current_user)