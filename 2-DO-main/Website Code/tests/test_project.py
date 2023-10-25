from website.models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Tests that the home page ("/") works properly
def test_home(client):
    # Create a user
    response = client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/")

    assert response.status_code == 302

#def test_logout(client):


# Testing User Creation
def test_sign_up(client, app):

    # "data" is a dictionary we can pass in data that we need to send to the database
    response = client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # More information on when to use app_context() and passing app as a param below all the tests
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "test@test.com"
        assert User.query.first().first_name == "TestFirstName"
        assert User.query.first().last_name == "TestLastName"
        assert check_password_hash(User.query.first().password, "testpassword") == True

# Attemping to login when the account does not exist
def test_invalid_login(client):
    
    response = client.post("/login", data={"email": "test@test.com", "password": "testpassword"})
    """ client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/") """

    assert response.status_code == 200 

# Attemping to login succesfully 
def test_valid_login(client):
    response = client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/")

    assert response.status_code == 302 

def test_task_creation(client, app):
    #Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    client.post("/", data={"title":"testtitle", "description":"test description", "date":"2003-10-10T12:30", "tag":"CSC678", "priority":"Low"})

    with app.app_context():
        assert Task.query.count() == 1
        assert Task.query.first().title == "testtitle"
        assert Task.query.first().description == "test description"
        assert Task.query.first().due_date == "2003-10-10 12:30"
        assert Task.query.first().tag == "CSC678"
        assert Task.query.first().priority == "Low"
        assert Task.query.first().status == 0

def test_task_deletion(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    initial_task_count = 0
    task_id = 0

    # Get the initial count of tasks in the database
    with app.app_context():
        initial_task_count = Task.query.count()

        # Get the ID of the task to delete
        task_id = Task.query.first().id

    # Send a request to delete the task
    client.get(f"/delete_task/{task_id}")

    # Get the count of tasks in the database after deletion
    updated_task_count = 0

    #Recount number of tasks
    with app.app_context():
        updated_task_count = Task.query.count()

    # Assert that the task count has decreased by 1
    assert updated_task_count == initial_task_count - 1

# Test the '/edit_task/<t>' route
def test_edit_task(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    # Get the task
    response = client.get("/edit_task/1")

    # Check if the response status code is 200 OK, which means the task was successfully retrieved
    assert response.status_code == 200

# Test the '/editform' route
def test_editform(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    # Edit the task
    response = client.post("/editform?taskid=1", data={"title": "New Title", "description": "New Description", "date": "2003-10-11 13:30", "tag": "NewTag", "priority": "High"})

    # Check if the response status code is 302 (redirect) or any other status code as expected
    assert response.status_code == 302  # Adjust this based on your expected behavior

    # Verify if the task attributes were updated in the database
    with app.app_context():
        task = Task.query.get(1)
        assert task.title == "New Title"
        assert task.description == "New Description"
        assert task.due_date == "2003-10-11 13:30"
        assert task.tag == "NewTag"
        assert task.priority == "High"

# Test the '/complete_task' route
def test_complete_task(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    # Prepare the JSON data
    data = {
        "task": 1,  # Task ID you want to complete
        "bool": True  # Use True to mark as complete or False to mark as incomplete
    }

    # Send a JSON POST request to complete the task
    response = client.post("/complete_task", data=json.dumps(data), content_type='application/json')

    # Check if the response status code is 200 OK or any other status code as expected
    assert response.status_code == 308  # Adjust this based on your expected behavior

    # Verify if the task status in the database was updated
    with app.app_context():
        task = Task.query.get(1)
        assert task.status == True  # Adjust this based on the data you sent (True for complete, False for incomplete)

        

"""
Tests that need to be run:
Sprint 1-2 Tests
✅ L-01 Ensure that a user can successfully create an account
✅ L-02 Ensure that a user can successfully login to their previously created account
✅ L-03 Ensure that a user can’t log into their account with an incorrect password
✅ L-04 Non-existent user

✅ T-01 Ensure that user can successfully add a task
✅ T-02 Ensure that the user can view a list of tasks
(DELETED) T-03 Ensure that a user can’t add a task due on a past date and/or time 
    - Some task managing applications, like Apple Reminders, allows for creation 
    of past tasks
    - Might just want to remove this test
✅ T-04 Ensure that a user can delete a task
✅ T-05 Ensure that a user can edit a task
✅ T-06 Ensure that a user can sort tasks by day and time

Sprint 3 Tests
T-07 Ensure that a user can filter by column values
    - Marked as T-06 incorrectly in Prep for Sprint 3 Doc
✅ T-08 Ensure that a user can mark tasks as complete/inc omplete
    - Marked as T-07 incorrectly in Prep for Sprint 3 Doc

"""


""" 
Notes:
In the given test case, the `app` parameter is used to provide the Flask application context to the test function. The `app` parameter is typically a fixture in Flask testing, and it represents the Flask application being tested. Let's break down the usage of `app` and the purpose of `app.app_context()`:

1. **`app` Parameter**:
   - `app` is a fixture provided to the test function through the use of a testing framework like `pytest`. It is essentially your Flask application, allowing you to interact with it in your test.
   - In your test case, it's used to create a client for making HTTP requests to your Flask application and to access the application context.

2. **`app.app_context()`**:
   - `app.app_context()` is used to establish an application context for the test. In Flask, the application context is a context that allows you to work with the application as if it were handling a real HTTP request.
   - The application context is typically required when you need to interact with the database or perform other operations that rely on the application context.
   - Inside the application context, you can access the database, session, and other application-specific resources.
   - It enables you to work with application-specific features and extensions (like your database) during the test without making actual HTTP requests.

In the test case, `app.app_context()` is used to create the necessary application context, which allows you to access and query the database using SQLAlchemy. This is why you can use `User.query` to query the database and perform assertions on the database records created during the test.

The combination of `app` as a parameter and `app.app_context()` allows you to interact with your Flask application and its associated resources, such as the database, during your test, creating a controlled and isolated testing environment.
 """



