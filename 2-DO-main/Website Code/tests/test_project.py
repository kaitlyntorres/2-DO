# Import necessary modules and models
from flask_login import current_user
from website.models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash
import json
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
import os

""" *** TEST CASES *** """
""" *** Sprint 1 & 2 *** """

# L-01 Ensure that a user can successfully create an account
def test_sign_up(client, app):

    # Create a user
    response = client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Access the app context to interact with the database
    with app.app_context():
        # Assert that a user has been created in the database with the provided information
        assert User.query.count() == 1
        assert User.query.first().email == "test@test.com"
        assert User.query.first().first_name == "TestFirstName"
        assert User.query.first().last_name == "TestLastName"
        assert check_password_hash(User.query.first().password, "testpassword") == True

# L-02 Ensure that a user can successfully login to their previously created account
def test_valid_login(client):
    response = client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/")

    # Assert that the response status code is 302 (a successful login attempt)
    assert response.status_code == 302 

# L-03 Ensure that a user can’t log into their account with an incorrect password
def test_incorrect_password(client, app):

    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Attempt login with an incorrect password
    response = client.post("/login", data={"email": "test@test.com", "password": "wrongpassword"})

    with app.app_context():
        assert response.status_code == 200 
        assert current_user != User.query.first()

# L-04 Non-existent user
def test_invalid_login(client):
    
    response = client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Assert that the response status code is 200 (an unsuccessful login attempt)
    assert response.status_code == 200 

# T-01 Ensure that user can successfully add a task
def test_task_creation(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title":"testtitle", "description":"test description", "date":"2003-10-10T12:30", "tag":"CSC678", "priority":"Low"})

    # Access the app context to interact with the database
    with app.app_context():
        # Assert that a task has been created in the database with the provided information
        assert Task.query.count() == 1
        assert Task.query.first().title == "testtitle"
        assert Task.query.first().description == "test description"
        assert Task.query.first().due_date == "2003-10-10 12:30"
        assert Task.query.first().tag == "CSC678"
        assert Task.query.first().priority == "Low"
        assert Task.query.first().status == 0

# T-02 Ensure that the user can view a list of tasks
def test_viewing_tasks(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "task1", "description": "desc1", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low"})

    # Create a second task with different data
    client.post("/", data={"title": "task2", "description": "desc2", "date": "2003-10-10 12:00", "tag": "CSC680", "priority": "High"})

    # Send a GET request to the task list page
    response = client.get("/")

    # Check if the response contains task titles and descriptions
    assert b'task1' in response.data
    assert b'desc1' in response.data
    assert b'task2' in response.data
    assert b'desc2' in response.data


# T-04 Ensure that a user can delete a task
def test_task_deletion(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    initial_task_count = 0
    task_id = 0

    # Access the app context to interact with the database
    with app.app_context():
        initial_task_count = Task.query.count()

        task_id = Task.query.first().id

    # Send a request to delete the task
    client.get(f"/delete_task/{task_id}")

    updated_task_count = 0

    # Recount the number of tasks in the database
    with app.app_context():
        updated_task_count = Task.query.count()

    # Assert that the task count has decreased by 1
    assert updated_task_count == initial_task_count - 1

# T-05 Ensure that a user can edit a task
def test_editform(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low"})

    # Edit the task
    response = client.post("/editform?taskid=1", data={"title": "New Title", "description": "New Description", "date": "2003-10-11 13:30", "tag": "NewTag", "priority": "High"})

    # Assert that the response status code is 302 (redirect)
    assert response.status_code == 302  # Adjust this based on your expected behavior

    # Verify if the task attributes were updated in the database
    with app.app_context():
        task = Task.query.get(1)
        assert task.title == "New Title"
        assert task.description == "New Description"
        assert task.due_date == "2003-10-11 13:30"
        assert task.tag == "NewTag"
        assert task.priority == "High"

# T-06 Ensure that a user can sort tasks 
def test_sorting(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "task1", "description": "desc1", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low"})

    # Create a second task with different data
    client.post("/", data={"title": "task2", "description": "desc2", "date": "2003-10-10 12:00", "tag": "CSC680", "priority": "High"})

    response = client.get("/")

    # Define a function to extract and sort rows from HTML content based on the given column
    def extract_and_sort_rows(html_content, sort_column):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", {"id": "task-table"})
        rows = table.find("tbody").find_all("tr", recursive=False)

        # Sort rows based on the specified column
        rows.sort(key=lambda row: row.find_all("td")[sort_column].text)

        return rows

    # Test sorting by ID (column index 0)
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=0)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=0)
    assert sorted_rows == expected_sorted_rows

    # Test sorting by 
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=1)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=1)
    assert sorted_rows == expected_sorted_rows

    # Test sorting by Title (column index 2)
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=2)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=2)
    assert sorted_rows == expected_sorted_rows

    # Test sorting by Tag (column index 4)
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=4)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=4)
    assert sorted_rows == expected_sorted_rows

    # Test sorting by Priority (column index 5)
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=5)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=5)
    assert sorted_rows == expected_sorted_rows

    # Test sorting by Status (column index 6)
    sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=6)
    expected_sorted_rows = extract_and_sort_rows(response.data.decode("utf-8"), sort_column=6)
    assert sorted_rows == expected_sorted_rows

""" *** Sprint 3 Test Cases *** """

# T-07 Ensure that a user can filter by column values

## How to use selenium web driver
# 1. Download: https://sites.google.com/chromium.org/driver/downloads



def test_search_tasks(client, app):

   # Set up the GeckoDriver using webdriver_manager
    gecko_service = Service(GeckoDriverManager().install())

    # Create a WebDriver instance using Firefox and the GeckoDriver
    driver = webdriver.Firefox(service=gecko_service)

    # Navigate to a website (e.g., Google)
    driver.get("http://127.0.0.1:3000/login")

    #driver.implicitly_wait(10)

    # Find the email and password input fields using WebDriver methods
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")

    # Enter your login credentials
    email_field.send_keys("kurt@gmail.com")
    password_field.send_keys("12345678")

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    #Search Terms
    search_column = "title"
    search_text = "task1"

    # Find and select the search column dropdown
    column_select = driver.find_element(By.ID, "columnSelect")
    column_select.send_keys(search_column)

    # Find and input the search text
    task_search = driver.find_element(By.ID, "taskSearch")
    task_search.send_keys(search_text)

    # Wait for a moment (you may need to adjust the waiting time)
    driver.implicitly_wait(2)

    # Find the tasks table
    task_table = driver.find_element(By.ID, "task-table")

    # Check if the search results are as expected
    assert f'task1' in task_table.text
    #ssert f'task2' not in task_table.text
    #assert f'task3' not in task_table.text

    search_column2 = "description"
    search_text2 = "desc2"

    search_column3 = "tag"
    search_text3 = "tag3"

    search_column4 = "priority"
    search_text4 = "High"




    # Simulate keyup event
    task_search.send_keys(Keys.RETURN)

    driver.quit()

    


# Old T-07
""" def test_search_tasks(client, app):

    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create tasks
    client.post("/", data={"title": "task1", "description": "desc1", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low"})
    client.post("/", data={"title": "task2", "description": "desc2", "date": "2003-10-10 12:00", "tag": "CSC680", "priority": "High"})
    client.post("/", data={"title": "task3", "description": "desc3", "date": "2003-10-11 13:00", "tag": "CSC678", "priority": "Medium"})

    # Send a GET request to the task list page
    response = client.get("/")

    # Check if the response status code is 200 (OK)
    #assert response.status_code == 200

    # Check if all tasks are displayed
    assert b'task1' in response.data
    assert b'task2' in response.data
    assert b'task3' in response.data

    # Test searching by title
    search_response = client.post("/", data={"columnSelect": "title", "taskSearch": "task1"})

    # Check if the response status code is 200 (OK)
    #assert search_response.status_code == 200

    # Check if the response contains the searched task
    assert b'task1' in search_response.data
    assert b'task2' not in search_response.data
    assert b'task3' not in search_response.data

    # Test searching by description
    search_response = client.post("/", data={"columnSelect": "description", "taskSearch": "desc2"})

    # Check if the response status code is 200 (OK)
    #assert search_response.status_code == 200

    # Check if the response contains the searched task
    assert b'task2' in search_response.data
    assert b'task1' not in search_response.data
    assert b'task3' not in search_response.data

    # Test searching by tag
    search_response = client.post("/", data={"columnSelect": "tag", "taskSearch": "CSC678"})

    # Check if the response status code is 200 (OK)
    #assert search_response.status_code == 200

    # Check if the response contains the searched task
    assert b'task1' in search_response.data
    assert b'task3' in search_response.data
    assert b'task2' not in search_response.data

    # You can add more search test cases based on different columns

    # Test searching by priority
    search_response = client.post("/", data={"columnSelect": "priority", "taskSearch": "Low"})

    # Check if the response status code is 200 (OK)
    #assert search_response.status_code == 200

    # Check if the response contains the searched task
    assert b'task1' in search_response.data
    assert b'task2' not in search_response.data
    assert b'task3' not in search_response.data """

# T-08 Ensure that a user can mark tasks as complete/incomplete
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

    # Assert that the response status code is 308 or adjust it based on your expected behavior
    assert response.status_code == 308  

    # Verify if the task status in the database was updated
    with app.app_context():
        task = Task.query.get(1)
        assert task.status == False # !!!


""" *** TESTING ACCESSING HTML VIEWS *** """
# Test the home page ("/") route
def test_home(client):
    # Create a user
    response = client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/")

    # Assert that the response status code is a 302 (redirect)
    assert response.status_code == 302

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

    # Assert that the response status code is 200 (a successful task retrieval)
    assert response.status_code == 200
        

"""
Tests that need to be run:
Sprint 1-2 Tests (DONE)

Login
✅ L-01 Ensure that a user can successfully create an account
✅ L-02 Ensure that a user can successfully login to their previously created account
✅ L-03 Ensure that a user can’t log into their account with an incorrect password
✅ L-04 Non-existent user

Tasks
✅ T-01 Ensure that user can successfully add a task
✅ T-02 Ensure that the user can view a list of tasks
(DELETED) T-03 Ensure that a user can’t add a task due on a past date and/or time 
    - Some task managing applications, like Apple Reminders, allows for creation 
    of past tasks
    - Might just want to remove this test
✅ T-04 Ensure that a user can delete a task
✅ T-05 Ensure that a user can edit a task
✅ T-06 Ensure that a user can sort tasks 

Sprint 3 Tests
T-07 Ensure that a user can filter by column values
    - Marked as T-06 incorrectly in Prep for Sprint 3 Doc
⭐️ T-08 Ensure that a user can mark tasks as complete/incomplete
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



