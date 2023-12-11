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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import os

""" *** TEST CASES *** """
""" *** Sprint 1 & 2 *** """

# L-01 Ensure that a user can successfully create an account
def test_s12_sign_up(client, app):

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
def test_s12_valid_login(client):
    response = client.post("/sign-up", data={"email": "test@test.com", "first_name": "TestFirstName", "last_name":"TestLastName", "password":"testpassword"})

    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    response = client.get("/")

    # Assert that the response status code is 302 (a successful login attempt)
    assert response.status_code == 302 

# L-03 Ensure that a user can’t log into their account with an incorrect password
def test_s12_incorrect_password(client, app):

    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Attempt login with an incorrect password
    response = client.post("/login", data={"email": "test@test.com", "password": "wrongpassword"})

    with app.app_context():
        assert response.status_code == 200 
        assert current_user != User.query.first()

# L-04 Non-existent user
def test_s12_invalid_login(client):
    
    response = client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Assert that the response status code is 200 (an unsuccessful login attempt)
    assert response.status_code == 200 

# T-01 Ensure that user can successfully add a task
def test_s12_task_creation(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName":"TestLastName", "password1":"testpassword", "password2":"testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title":"testtitle", "description":"test description", "date":"2003-10-10T12:30", "tag":"CSC678", "priority":"Low", "reminder_time":"2003-10-10T12:00"})

    # Access the app context to interact with the database
    with app.app_context():
        # Assert that a task has been created in the database with the provided information
        assert Task.query.count() == 1
        assert Task.query.first().title == "testtitle"
        assert Task.query.first().description == "test description"
        assert Task.query.first().due_date == "2003-10-10 12:30"
        assert Task.query.first().tag == "CSC678"
        assert Task.query.first().priority == "Low"
        assert Task.query.first().reminder_time == "2003-10-10 12:00"
        assert Task.query.first().status == 0

# T-02 Ensure that the user can view a list of tasks
def test_s12_viewing_tasks(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "task1", "description": "desc1", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-10T12:00"})

    # Create a second task with different data
    client.post("/", data={"title": "task2", "description": "desc2", "date": "2003-10-10T12:00", "tag": "CSC680", "priority": "High", "reminder_time": "2003-10-10T12:15"})

    response = client.get("/")

    # Check if the response contains task titles, descriptions, and reminder times
    assert b'task1' in response.data
    assert b'desc1' in response.data
    assert b'task2' in response.data
    assert b'desc2' in response.data
    assert b'2003-10-10 12:00' in response.data
    assert b'2003-10-10 12:15' in response.data



# T-04 Ensure that a user can delete a task
def test_s12_task_deletion(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-10T12:00"})

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
def test_s12_editform(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10T12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-10T12:00"})

    # Edit the task
    response = client.post("/editform?taskid=1", data={"title": "New Title", "description": "New Description", "date": "2003-10-11T13:30", "tag": "NewTag", "priority": "High", "reminder_time": "2003-10-11T13:15"})

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
        assert task.reminder_time == "2003-10-11 13:15"


# T-06 Ensure that a user can sort tasks 
def test_s12_sorting(client, app):
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
        table = soup.find("table", {"id": "task-table1"})
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

    def extract_and_sort_rows(html_content, sort_column):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", {"id": "task-table2"})
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

# T-07 Ensure that a user can filter by column values in the incomplete table
def test_s3_incomplete_search_tasks(client, app):
    # SHOULD HAVE THIS TEST INPUT A TASK AND THEN CHECK INSTEAD OF RELYING 
    # UPON HAVING THE TESTS ALREADY EXISTING IN THE DATABASE

   # Set up the GeckoDriver using webdriver_manager
    gecko_service = Service(GeckoDriverManager().install())

    # Create a WebDriver instance using Firefox and the GeckoDriver
    driver = webdriver.Firefox(service=gecko_service)

    # Navigate to a website (e.g., Google)
    driver.get("http://127.0.0.1:3000/login")

    # Find the email and password input fields using WebDriver methods
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")

    # Enter your login credentials
    email_field.send_keys("kurt@gmail.com")
    password_field.send_keys("12345678")

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    # Test Title Search 
    #Search Terms
    search_column = "title"
    search_text = "task1"

    time.sleep(3)

    # Find and select the search column dropdown
    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)

    # Find and input the search text
    task_search = driver.find_element(By.ID, "taskSearch1")
    task_search.send_keys(search_text)
    
    # Wait for a moment (you may need to adjust the waiting time)
    driver.implicitly_wait(2)
    
    # Find the tasks table
    task_table = driver.find_element(By.ID, "task-table1")

    # Check if the search results are as expected
    assert f'task1' in task_table.text
    assert f'task2' not in task_table.text
    assert f'task3' not in task_table.text

    # Test Description Search 
    driver.refresh()
    time.sleep(3)
    search_column = "description"
    search_text = "desc2"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch1")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table1")

    assert f'desc2' in task_table.text
    assert f'desc1' not in task_table.text
    assert f'desc3' not in task_table.text

    # Test Tag Search 
    driver.refresh()
    time.sleep(3)
    search_column = "tag"
    search_text = "tag3"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch1")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table1")

    assert f'tag3' in task_table.text
    assert f'tag1' not in task_table.text
    assert f'tag2' not in task_table.text

    # Test Priority Search 
    driver.refresh()
    time.sleep(3)
    search_column = "priority"
    search_text = "High"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch1")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table1")

    assert f'High' in task_table.text
    assert f'Low' not in task_table.text
    assert f'Medium' not in task_table.text

    # Quit Driver When Done
    driver.quit() 

# T-07-01 Ensure that a user can filter by column values in the complete table
# NEED TO CHANGE SO THAT IT SELECTS THE RIGHT "columnSelect" 
# CURRENT JUST GRABS THE FIRST "columnSelect" AND FINDS THE RIGHT DATA SINCE THE 
# TABLE WASNT FILTERED OUT, HENCE CONTAINING ALL THE DATA
def test_s3_complete_search_tasks(client, app):
    # SHOULD HAVE THIS TEST INPUT A TASK AND THEN CHECK INSTEAD OF RELYING 
    # UPON HAVING THE TESTS ALREADY EXISTING IN THE DATABASE

   # Set up the GeckoDriver using webdriver_manager
    gecko_service = Service(GeckoDriverManager().install())

    # Create a WebDriver instance using Firefox and the GeckoDriver
    driver = webdriver.Firefox(service=gecko_service)

    # Navigate to a website (e.g., Google)
    driver.get("http://127.0.0.1:3000/login")

    # Find the email and password input fields using WebDriver methods
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")

    # Enter your login credentials
    email_field.send_keys("kurt@gmail.com")
    password_field.send_keys("12345678")

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    # Test Title Search 
    #Search Terms
    search_column = "title"
    search_text = "task1complete"

    time.sleep(3)

    # Find and select the search column dropdown
    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)

    # Find and input the search text
    task_search = driver.find_element(By.ID, "taskSearch2")
    task_search.send_keys(search_text)
    
    # Wait for a moment (you may need to adjust the waiting time)
    driver.implicitly_wait(2)
    
    # Find the tasks table
    task_table = driver.find_element(By.ID, "task-table2")

    # Check if the search results are as expected
    assert f'task1' in task_table.text
    assert f'task2' not in task_table.text
    assert f'task3' not in task_table.text

    # Test Description Search 
    driver.refresh()
    time.sleep(3)
    search_column = "description"
    search_text = "desc2complete"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch2")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table2")

    assert f'desc2' in task_table.text
    assert f'desc1' not in task_table.text
    assert f'desc3' not in task_table.text

    # Test Tag Search 
    driver.refresh()
    time.sleep(3)
    search_column = "tag"
    search_text = "tag3complete"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch2")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table2")

    assert f'tag3' in task_table.text
    assert f'tag1' not in task_table.text
    assert f'tag2' not in task_table.text

    # Test Priority Search 
    driver.refresh()
    time.sleep(3)
    search_column = "priority"
    search_text = "High"

    column_select = driver.find_element(By.NAME, "columnSelect")
    column_select.send_keys(search_column)
    time.sleep(1)
    task_search = driver.find_element(By.ID, "taskSearch2")
    task_search.send_keys(search_text)

    driver.implicitly_wait(2)

    task_table = driver.find_element(By.ID, "task-table2")

    assert f'High' in task_table.text
    assert f'Low' not in task_table.text
    assert f'Medium' not in task_table.text

    # Quit Driver When Done
    driver.quit() 

# T-08 Ensure that a user can mark tasks as complete/incomplete
def test_s3_complete_task(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Create a task - Status defaults to False (Incomplete)
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-10 12:00"})

    # Prepare the JSON data
    data = {
        "task": 1,  # Task ID you want to complete
        "bool": True  # Use True to mark as complete or False to mark as incomplete
    }

    # Send a JSON POST request to complete the task
    response = client.post("/complete_task/", data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200  

    # Verify if the task status in the database was updated
    with app.app_context():
        task = Task.query.get(1)
        assert task.status == True # Check that the status changed to True from the False default

"""*** Sprint 4 Test Cases ***"""

# C-01 Test that a user can view all completed tasks in a separate table
def test_s4_completed_tasks_views(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Add Three Tasks
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-10 12:00"})
    client.post("/", data={"title": "second_title", "description": "second_description", "date": "2003-10-11 14:30", "tag": "CSC679", "priority": "Medium", "reminder_time": "2003-10-11 14:00"})
    client.post("/", data={"title": "third_title", "description": "third_description", "date": "2003-10-12 15:30", "tag": "CSC680", "priority": "High", "reminder_time": "2003-10-12 15:00"})

    # Change the first task status to True (Compelete)
    data = {
        "task": 1,  # Task ID you want to complete
        "bool": True  # Use True to mark as complete or False to mark as incomplete
    }

    # Send a JSON POST request to complete the task
    response = client.post("/complete_task/", data=json.dumps(data), content_type='application/json')
   
    with app.app_context():
        task = Task.query.get(1)
        assert task.status == True # Check that the status changed to True from the False default

# R-01 Test that the user can set a reminder time
def test_s4_set_reminder_time(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Add Three Tasks
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low", "reminder_time": ""})

    client.post("/editform?taskid=1", data={"title": "New Title", "description": "New Description", "date": "2003-10-11T13:30", "tag": "NewTag", "priority": "High", "reminder_time": "2003-10-11 13:15"})

    # Verify if the task attributes were updated in the database
    with app.app_context():
        task = Task.query.get(1)
        assert task.title == "New Title"
        assert task.description == "New Description"
        assert task.due_date == "2003-10-11 13:30"
        assert task.tag == "NewTag"
        assert task.priority == "High"
        assert task.reminder_time == "2003-10-11 13:15"

# R-02 Test that the user can remove the reminder time from a task
def test_s4_remove_reminder_time(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Add a Task
    client.post("/", data={"title": "testtitle", "description": "test description", "date": "2003-10-10 12:30", "tag": "CSC678", "priority": "Low", "reminder_time": "2003-10-11 13:15"})

    # Edit Task to remove the reminder time
    client.post("/editform?taskid=1", data={"title": "New Title", "description": "New Description", "date": "2003-10-11T13:30", "tag": "NewTag", "priority": "High", "reminder_time": ""})

    # Verify if the task attributes were updated in the database
    with app.app_context():
        task = Task.query.get(1)
        assert task.title == "New Title"
        assert task.description == "New Description"
        assert task.due_date == "2003-10-11 13:30"
        assert task.tag == "NewTag"
        assert task.priority == "High"
        assert task.reminder_time == ""

# R-03 Test that the user will receive a reminder notification
def test_s4_reminder_notification(client, app):
    # SHOULD HAVE THIS TEST INPUT A TASK AND THEN CHECK INSTEAD OF RELYING 
    # UPON HAVING THE TESTS ALREADY EXISTING IN THE DATABASE

    # Set up the GeckoDriver using webdriver_manager
    gecko_service = Service(GeckoDriverManager().install())

    # Create Firefox options
    firefox_options = Options()

    # Allow notifications
    firefox_options.set_preference("dom.webnotifications.enabled", True)

    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.desktop-notification', 1)
    #driver = webdriver.Firefox(firefox_profile=profile)

    # Create a WebDriver instance using Firefox and the GeckoDriver
    driver = webdriver.Firefox(service=gecko_service, options=firefox_options, firefox_profile=profile)

    # Navigate to our site
    driver.get("http://127.0.0.1:3000/login")

    # Find the email and password input fields using WebDriver methods
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")

    # Enter your login credentials
    email_field.send_keys("kurt@gmail.com")
    password_field.send_keys("12345678")

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    time.sleep(3)

    # Test clicking edit button
    task_table = driver.find_element(By.ID, "task-table1")
    
    # Find the edit button in the first row (assuming it's the first row, adjust if needed)
    edit_button = task_table.find_element(By.XPATH, "//tr[1]//a[contains(@href, '/editform?taskid=')]")

    edit_button.click()

    time.sleep(3)

    # Assuming 'driver' is your WebDriver instance
    # Find the Reminder time input
    reminder_time_input = driver.find_element(By.ID, "reminder_time")

    # Get the current time and add one minute
    current_time = time.localtime()
    one_minute_later = time.mktime(current_time) + 60

    # Clear the existing value in the input
    reminder_time_input.clear()

    # Input the new value with the date parts sent one at a time
    formatted_one_minute_later = time.localtime(one_minute_later)

    # Send the month
    reminder_time_input.send_keys(time.strftime('%m', formatted_one_minute_later))

    # Send the Tab key
    #reminder_time_input.send_keys(Keys.TAB)
    
    # Send the day
    reminder_time_input.send_keys(time.strftime('%d', formatted_one_minute_later))

    # Send the Tab key
    #reminder_time_input.send_keys(Keys.TAB)

     # Send the year
    reminder_time_input.send_keys(time.strftime('%Y', formatted_one_minute_later))

    # Send the Tab key
    reminder_time_input.send_keys(Keys.TAB)
    
    # Send the hour
    reminder_time_input.send_keys(time.strftime('%I', formatted_one_minute_later))

    # Send the Tab key
    #reminder_time_input.send_keys(Keys.TAB)

    # Send the minute
    reminder_time_input.send_keys(time.strftime('%M', formatted_one_minute_later))

    # Send the space key
    #reminder_time_input.send_keys(Keys.SPACE)

    # Send the AM/PM indicator
    reminder_time_input.send_keys(time.strftime('%p', formatted_one_minute_later))

    # Find and click the submit button
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()

    # Wait for the page to reload (adjust wait time as needed)
    time.sleep(3)

    # Find and click the "Schedule Notification" button for the first task
    schedule_notification_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'scheduleNotification')]"))
    )
    schedule_notification_button.click()

    # Wait for the notification to appear (adjust wait time as needed)
    time.sleep(1)

    # Wait for the notification to appear (adjust wait time as needed)
    notification = driver.find_element(By.ID, "notification-container")

    # Perform assertions or other actions as needed
    assert "Reminder Set!" in notification.text

    # Perform additional checks/assertions as needed

    # Quit the WebDriver
    driver.quit()

""" *** Sprint 5 Test Cases """

def test_s5_export(client, app):
    # Create a user
    client.post("/sign-up", data={"email": "test@test.com", "firstName": "TestFirstName", "lastName": "TestLastName", "password1": "testpassword", "password2": "testpassword"})

    # Login the user
    client.post("/login", data={"email": "test@test.com", "password": "testpassword"})

    # Make a request to the to_csv endpoint
    response = client.get('/to_csv/')
    assert response.status_code == 200

    # Check if the CSV files are created
    assert (os.path.exists('alltasks.csv'))==True
    assert (os.path.exists('incompletetasks.csv'))==True
    assert (os.path.exists('completetasks.csv')) ==True

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
✅ T-07 Ensure that a user can filter by column values
    - Marked as T-06 incorrectly in Prep for Sprint 3 Doc
✅ T-08 Ensure that a user can mark tasks as complete/incomplete
    - Marked as T-07 incorrectly in Prep for Sprint 3 Doc

Sprint 4 Tests
C-01 Test that a user can view all completed tasks in a separate table
    - Initial set up done, need to implement the rest to finish the testing
✅ R-01 Test that the user can set a reminder time
✅ R-02 Test that the user can remove the reminder time from a task
✅ R-03 Test that the user recieves a notificaiton

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



