import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import os

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

#driver.implicitly_wait(3)
time.sleep(5)
#driver.get("http://127.0.0.1:3000/")

page_html = driver.page_source
print(page_html)

# Find and select the search column dropdown
#select_element = Select(driver.find_element(By.ID, "columnSelect"))
column_select = driver.find_element(By.NAME, "columnSelect")
column_select.send_keys(search_column)
#select_element.select_by_value("title")

# Find and input the search text
task_search = driver.find_element(By.ID, "taskSearch")
task_search.send_keys(search_text)

# Wait for a moment (you may need to adjust the waiting time)
driver.implicitly_wait(2)

# Find the tasks table
task_table = driver.find_element(By.ID, "task-table")

# Check if the search results are as expected
assert f'task1' in task_table.text

# Perform actions on the web page using the driver
# ...

# Don't forget to close the driver when you're done
#driver.quit()

""" # Get the current directory (the directory where your Python script is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the Firefox GeckoDriver executable in the current directory
geckodriver_path = os.path.join(current_directory, "geckodriver")

# Create a WebDriver instance using Firefox
driver = webdriver.Firefox(executable_path=geckodriver_path)

# Navigate to the login page
driver.get("http://127.0.0.1:3000/login")  # Replace with the actual URL of your login page

driver.implicitly_wait(10)

# Find the email and password input fields using WebDriver methods
email_field = driver.find_element_by_id("email")
password_field = driver.find_element_by_id("password")

# Enter your login credentials
email_field.send_keys("kurt@gmail.com")
password_field.send_keys("12345678")

# Submit the login form
password_field.send_keys(Keys.RETURN) """