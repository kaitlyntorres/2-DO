from . import db #imports from website our db object
from flask_login import UserMixin #Helps logs users in
from sqlalchemy.sql import func

#Creating Database Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True) #ID will be incremented on its own
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #Foreign key is the user.id that created the task
    title = db.Column(db.String(1000)) #This will be the title of the task that was created
    description = db.Column(db.String(10000)) #The user can add notes and detail to tasks that they are creating
    ## MIGHT HAVE TO CHANGE HOW THE TIME & DATE TYPES ARE HELD IN THE DATABASE
    # MIGHT CHANGE TO STRING FOR THE MEAN TIME
    #due_time = db.Column(db.DateTime()) # HH:MM:SS.ssss format
    due_date = db.Column(db.String(40)) # YYYY-MM-DD Format || The HTML is in MM/
    tag = db.Column(db.String(6)) 
    priority = db.Column(db.String(6)) #should only be 'Low', 'Medium', 'High'
    status = db.Column(db.Boolean, default=False) #False for incomplete, True for complete
    reminder_time = db.Column(db.String(40))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #ID will be incremented on its own
    email = db.Column(db.String(150), unique=True) #No user can have the same emial as another user that exists
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    tasks = db.relationship('Task') #Tells Flask and SQL to add this relationship to task.id