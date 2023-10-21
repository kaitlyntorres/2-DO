from flask import Blueprint, render_template, request, flash,redirect, url_for
from flask_login import login_required, current_user
from .models import Task
from . import db
import json
import jsonify
import sys


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
        new_task = Task(title=title,user_id=current_user.id,description=description,due_date=date,tag=tag,priority=priority)
        db.session.add(new_task)
        db.session.commit()
    return render_template("home.html", user=current_user)


@views.route('/delete_task/<t>')
@login_required
def delete_task(t):
    task = Task.query.filter_by(id=t).first()
    if task:
        msg_text = '%s successfully removed' % str(task)
        db.session.delete(task)
        db.session.commit()
        flash(msg_text)
    return redirect(url_for('views.home'))

@views.route('/edit_task/<t>')
@login_required
def edit_task(t):
    task = Task.query.filter_by(id=t).first()
    return render_template('editform.html',task=task, user=current_user)

@views.route('/editform', methods = ['GET', 'POST'])
@login_required
def editform():
    taskid=request.args.get('taskid',None)

    task = Task.query.filter_by(id=taskid).first()

    if request.method == "POST":
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.date = request.form.get('date')
        task.tag = request.form.get('tag')
        task.priority = request.form.get('priority')

        db.session.commit()
        return redirect(url_for('views.home'))

    return render_template("editform.html", user=current_user)


@views.route('/complete_task/',methods=["POST"])
@login_required
def complete_task():
    #grabs dict from home.html
    output=request.get_json()
    #retrieves task id
    task_id= output.get('task')
    #retrieves boolean value
    bool=output.get('bool')
    #grabs row in db where task = id
    task = Task.query.filter_by(id=task_id).first()
    #changes status of row to the boolean passed in
    task.status = bool
    db.session.commit()
   
    return render_template("editform.html", user=current_user)

    

    





