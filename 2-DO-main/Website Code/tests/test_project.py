from website.models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash

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

    hashed_password = generate_password_hash("testpassword", method='sha256')

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

# NEED TO FIND A WAY TO GET A USER LOGGED IN SO THAT WE CAN ADD TASKS
def test_task_creation(client, app):
    client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    client.post("/", data={"title":"testtitle", "description":"test description", "date":"2003-10-10T12:30", "tag":"CSC678", "priority":"Low"})

    with app.app_context():
        assert Task.query.count() == 1
        assert Task.query.first().title == "testtitle"
        assert Task.query.first().description == "test description"
        assert Task.query.first().date == "2003-10-10 12:30"
        assert Task.query.first().tag == "CSC678"
        assert Task.query.first().priority == "Low"
        assert Task.query.first().status == 0
        


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



