from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Task
from . import db
import json
import jsonify

#This application has a bunch of URLs defined here so that we can have our views defined in several files and not a single one
#This is what Blueprints allows us to do
views = Blueprint('views', __name__)

#Decorator, calls on the function when this route is hit
@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        tag = request.form.get('tag')
        priority = request.form.get('priority')


        ## NEED TO ADD NEW TASK TO DATABASE
        # EXAMPLE IS IN AUTH.PY, ALSO LOOK AT OLD VIEWS.PY ON CSC 530 SUPPORT TICKET WEBSITE GITHUB
        new_task = Task(title=title,user_id=current_user.id,description=description,due_date=date,tag=tag,priority=priority,status=False)
        db.session.add(new_task)
        db.session.commit()
    return render_template("home.html", user=current_user)

""" 
@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    #Prevents Users who do not own the note from deleting it
    if note:
        if note.user_id == current_user.id or current_user.admin_access == True:
            db.session.delete(note)
            db.session.commit()

    return jsonify({}) """


