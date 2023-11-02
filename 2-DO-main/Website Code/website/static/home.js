// Store the current sorting direction for each column
var sortDirections = Array(7).fill(1); // 1 for ascending, -1 for descending

function sortTable(num) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("task-table");
    switching = true;
    sortDirections[num] *= -1;

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[num];
            y = rows[i + 1].getElementsByTagName("TD")[num];

            if (num == 0 || num == 1) {
                var xValue = Number(x.innerHTML);
                var yValue = Number(y.innerHTML);
            } else if (num == 5) {
                var xValue = getPriorityValue(x.innerHTML);
                var yValue = getPriorityValue(y.innerHTML);
            } else if (num == 6) {
                // Column 6 (Status): Custom sorting based on incomplete/complete
                var xValue = getStatusValue(x.firstChild);
                var yValue = getStatusValue(y.firstChild);
            } else {
                var xValue = x.innerHTML.toLowerCase();
                var yValue = y.innerHTML.toLowerCase();
            }

            // Custom sorting for the "Status" column
            if (xValue === yValue) {
                continue;
            } else if (xValue < yValue) {
                if (sortDirections[num] === 1) {
                    shouldSwitch = true;
                    break;
                }
            } else {
                if (sortDirections[num] === -1) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

function getStatusValue(checkbox) {
    // Custom sorting for "Status" column
    return checkbox.value === "True" ? 1 : 0; // 1 for complete (True), 0 for incomplete (False)
}

/* <!-- <script>

  function sortTable(num) {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("task-table");
  switching = true;

  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;

    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;

      x = rows[i].getElementsByTagName("TD")[num];
      y = rows[i + 1].getElementsByTagName("TD")[num];
      // Check if the two rows should switch place:
      if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
        // If so, mark as a switch and break the loop:
        shouldSwitch = true;
        break;
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
    }
  }
}
</script> -->
<!-- THIS IS A TEMP CHANGE FOR SORTING --> */


// Helper function to convert priority text to sortable value
function getPriorityValue(priority) {
    switch (priority) {
        case "Low":
            return 1;
        case "Medium":
            return 2;
        case "High":
            return 3;
        default:
            return 0; // Handle other cases if necessary
    }
}




//Checkbox is checked if task is complete. Bool value and task id get passed to Flask to update bool in db
function checkComplete(t) {
    //grabs checkbox
    checkbox = document.getElementById(t)
    // True if checkbox is checked, false if checkbox is not checked
    var bool = checkbox.checked
    var xmlhttp = new XMLHttpRequest(); // new HttpRequest instance 
    //where we pass data in views.py
    var theUrl = "/complete_task/";
    xmlhttp.open("POST", theUrl);
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    //passes data as dict
    xmlhttp.send(JSON.stringify({
        'task': t,
        'bool': bool
    }));
}

function showHelpPage() {
    // Redirect the user to the help page URL
    window.location.href = "/help"; // Replace "/help" with your actual help page URL
}




var searchColumn = "title"; // Default search column

function changeSearchColumn() {
    var columnSelect = document.getElementById("columnSelect");
    searchColumn = columnSelect.options[columnSelect.selectedIndex].value;
    searchTasks();
}

function searchTasks() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("taskSearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("task-table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[2]; // Index 2 is the Title column, adjust it as needed
        if (searchColumn === "description") {
            td = tr[i].getElementsByTagName("td")[3]; // Index 3 is the Description column
        } else if (searchColumn === "tag") {
            td = tr[i].getElementsByTagName("td")[4]; // Index 4 is the Tag column
        } else if (searchColumn === "priority") {
            td = tr[i].getElementsByTagName("td")[5]; // Index 5 is the Priority column
        } else if (searchColumn === "status") {
            td = tr[i].getElementsByTagName("td")[6]; // Index 6 is the Status column
        }

        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function showNotificationMessage(message, category) {
    const notificationContainer = document.getElementById('notification-container');

    // Create a new notification element
    const notification = document.createElement('div');
    notification.classList.add('notification', category); // Add CSS classes for styling

    // Set the content of the notification
    notification.innerText = message;

    // Append the notification to the container
    notificationContainer.appendChild(notification);

    // Auto-hide the notification after a few seconds (adjust as needed)
    setTimeout(() => {
        notification.remove();
    }, 5000); // 5000 milliseconds (5 seconds) in this example
}


function scheduleNotification(task_id) {
    // Check if the browser supports the Notification API
    if ("Notification" in window) {
        // Check the current permission status
        if (Notification.permission === 'granted') {
            // Permission has already been granted
            showNotification(task_id);
        } else if (Notification.permission !== 'denied') {
            // Request permission from the user
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    // Permission granted, show the notification
                    showNotification(task_id);
                }
            });
        } else {
            // Permission is denied, inform the user
            alert("Notification permission is denied. You won't receive notifications.");
        }
    } else {
        // The browser doesn't support the Notification API
        alert('Your browser does not support notifications.');
    }
}

function showNotification(task_id) {
    // Fetch task data for the given task_id
    fetch(`/get_task/${task_id}`)
        .then(response => response.json())
        .then(data => {
            if (data.id !== undefined) {
                // Task data is valid
                const taskName = data.title;
                const taskDescription = data.description;
                const reminderTime = data.reminder_time;

                // Convert the reminderTime string to a Date object
                const reminderTimeDate = new Date(reminderTime);

                // Get the timestamp from the reminderTimeDate
                const reminderTimestamp = reminderTimeDate.getTime();

                // Get the current timestamp
                const now = new Date().getTime();

                // Calculate the time difference in milliseconds
                const timeUntilReminder = reminderTimestamp - now;

                if (timeUntilReminder <= 0) {
                    alert("Invalid reminder time");
                    return;
                }

                showNotificationMessage('Reminder Set!', 'success');

                setTimeout(() => {
                    if (Notification.permission === 'granted') {
                        const notification = new Notification(taskName, {
                            body: taskDescription,
                            icon: 'your_icon.png' // You can specify your own icon
                        });
                    } else if (Notification.permission !== 'denied') {
                        Notification.requestPermission().then(permission => {
                            if (permission === 'granted') {
                                const notification = new Notification(taskName, {
                                    body: taskDescription,
                                    icon: 'your_icon.png' // You can specify your own icon
                                });
                            }
                        });
                    }
                }, timeUntilReminder);
            } else {
                alert('Task not found');
            }
        })
        .catch(error => console.error('Error:', error));
}


function moveToCompleted(checkbox) {
    const taskRow = checkbox.parentElement.parentElement; // Get the task row
    const completedTasksTable = document.getElementById("completed-tasks").getElementsByTagName("tbody")[0];

    // Clone the task row and append it to the completed tasks table
    completedTasksTable.appendChild(taskRow);

    // Show the completed tasks table
    document.getElementById("completed-tasks").style.display = "block";

    // Remove the checkbox's change event listener
    checkbox.removeEventListener("change", moveToCompleted);

    // Attach a new change event listener to mark the task as incomplete
    checkbox.addEventListener("change", moveToIncomplete);
}


  function moveToIncomplete(checkbox) {
    const taskRow = checkbox.parentElement.parentElement; // Get the task row
    const incompleteTasksTable = document.getElementById("incomplete-tasks").getElementsByTagName("tbody")[0];

    // Clone the task row and append it to the incomplete tasks table
    incompleteTasksTable.appendChild(taskRow);
  }

  // Attach event listeners to the checkboxes for marking tasks as complete
  const checkboxes = document.getElementById("incomplete-tasks").getElementsByTagName("input");
  for (const checkbox of checkboxes) {
    checkbox.addEventListener("change", function () {
      if (this.checked) {
        moveToCompleted(this);
      }
    });
  }

  // Attach event listeners to the checkboxes in the completed tasks table for marking tasks as incomplete
  const completedCheckboxes = document.getElementById("completed-tasks").getElementsByTagName("input");
  for (const checkbox of completedCheckboxes) {
    checkbox.addEventListener("change", function () {
      if (!this.checked) {
        moveToIncomplete(this);
      }
    });
  }