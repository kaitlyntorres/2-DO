from flask import Blueprint, render_template, request, flash,redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
import datetime
from .models import Task
from . import db
import json
import sys
import csv
import os


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
        date = request.form.get('date') #'YYYY-MM-DDTHH:MM'
        tag = request.form.get('tag') 
        priority = request.form.get('priority') #'Low', 'Medium', 'High'
        reminder_time = request.form.get('reminder_time')


        # Fixing Date Format || Switing from 'YYYY-MM-DDTHH:MM' to 'YYYY-MM-DD HH:MM'
        formatted_date = date.replace("T", " ")
        formatted_reminder_time = reminder_time.replace("T", " ")

        ## NEED TO ADD NEW TASK TO DATABASE
        # EXAMPLE IS IN AUTH.PY, ALSO LOOK AT OLD VIEWS.PY ON CSC 530 SUPPORT TICKET WEBSITE GITHUB
        new_task = Task(title=title,user_id=current_user.id,description=description,due_date=formatted_date,tag=tag,priority=priority, reminder_time=formatted_reminder_time)
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

        # Fixing Date Format || Switing from 'YYYY-MM-DDTHH:MM' to 'YYYY-MM-DD HH:MM'
        formatted_date = request.form.get('date').replace("T", " ")
        formatted_reminder_time = request.form.get('reminder_time').replace("T", " ")

        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.due_date = formatted_date
        task.tag = request.form.get('tag')
        task.priority = request.form.get('priority')
        task.reminder_time = formatted_reminder_time

        db.session.commit()
        return redirect(url_for('views.home'))

    return render_template("editform.html", user=current_user, task=task)


@views.route('/complete_task/', methods=["POST"])
@login_required
def complete_task():
    # Grabs the JSON data from home.html
    output = request.get_json()
    # Retrieves task id
    task_id = output.get('task')
    
    # Grabs the row in the database where task = id
    task = Task.query.filter_by(id=task_id).first()

    # Toggles the status of the task (complementing the boolean value)
    task.status = not task.status

    db.session.commit()

    return render_template("home.html", user=current_user)


@views.route('/get_task/<task_id>')
def get_task(task_id):
    # Retrieve the task data based on task_id
    task = Task.query.get(task_id)
    
    task_data = {
        'id': task.id,
        'user_id': task.user_id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date,
        'tag': task.tag,
        'priority': task.priority,
        'status': task.status,
        'reminder_time': task.reminder_time
    }

    return jsonify(task_data)


@views.route('/help')
def help():
    # Add any necessary data to pass to the help page here
    return render_template('help.html', user=current_user)

#exports task to csv
@views.route('/to_csv/')
@login_required
def to_csv():
    with open('alltasks.csv','w',newline='') as csv_file:
        write_csv=csv.writer(csv_file,delimiter=',')
        #creates header row
        write_csv.writerow(['ID','Date and Time','Title','Description','Tag','Priority','Status','Reminder Time'])
        #grabs all rows in Task Table
        rows = Task.query.all()
        #rows=Task.query.filter(Task.status.is_(False)).all()
        #rows=.query(fellowers).filter_by(id = fellow_id).one()
        #writes each row to csv
        for task in rows:
            write_csv.writerow([task.id,task.due_date,task.title,task.description,task.tag,task.priority,task.status,task.reminder_time])


    with open('incompletetasks.csv','w',newline='') as csv_file:
        write_csv=csv.writer(csv_file,delimiter=',')
        #creates header row
        write_csv.writerow(['ID','Date and Time','Title','Description','Tag','Priority','Status','Reminder Time'])
        #grabs all rows in Task Table
        #rows = Task.query.all()
        rows=Task.query.filter(Task.status.is_(False)).all()
        #rows=.query(fellowers).filter_by(id = fellow_id).one()
        #writes each row to csv
        for task in rows:
            write_csv.writerow([task.id,task.due_date,task.title,task.description,task.tag,task.priority,task.status,task.reminder_time])


        with open('completetasks.csv','w',newline='') as csv_file:
            write_csv=csv.writer(csv_file,delimiter=',')
            #creates header row
            write_csv.writerow(['ID','Date and Time','Title','Description','Tag','Priority','Status','Reminder Time'])
            #grabs all rows in Task Table
            #rows = Task.query.all()
            rows=Task.query.filter(Task.status.is_(True)).all()
            #rows=.query(fellowers).filter_by(id = fellow_id).one()
            #writes each row to csv
            for task in rows:
                write_csv.writerow([task.id,task.due_date,task.title,task.description,task.tag,task.priority,task.status,task.reminder_time])
 
    #returns it as a download with user's first and last name
    filename=str(current_user.first_name)+" "+str(current_user.last_name)+ "'s Tasks.xlsx"

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df1= pd.read_csv('alltasks.csv')
    df1.to_excel(writer, sheet_name=os.path.basename('All Tasks'))
    df2= pd.read_csv('incompletetasks.csv')
    df2.to_excel(writer, sheet_name=os.path.basename('Incomplete Tasks'))
    df3= pd.read_csv('completetasks.csv')
    df3.to_excel(writer, sheet_name=os.path.basename('Complete Tasks'))
    writer.close()

    return send_file(os.path.abspath(filename),
                     mimetype='text/csv',
                     download_name=filename,
                     as_attachment=True)

    

    





