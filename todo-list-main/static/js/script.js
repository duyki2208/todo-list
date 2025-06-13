// API endpoints
const API = {
  tasks: "/api/tasks",
  task: (id) => `/api/tasks/${id}`,
};

let currentSection = "myDay";

// Function to fetch tasks from the server
async function fetchTasks() {
  try {
    const response = await fetch(API.tasks);
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    const tasks = await response.json();
    console.log("Raw tasks from server:", tasks); // Debug log

    // If tasks is empty or not an object, return empty array
    if (!tasks || typeof tasks !== "object") {
      console.log("No tasks or invalid tasks data");
      return [];
    }

    // Convert tasks object to array and ensure all required fields
    const taskArray = Object.entries(tasks)
      .map(([id, task]) => {
        if (!task || typeof task !== "object") {
          console.warn("Invalid task data:", task);
          return null;
        }
        return {
          ...task,
          id: id, // Ensure id is included
        };
      })
      .filter((task) => task !== null); // Remove any invalid tasks

    console.log("Processed tasks:", taskArray); // Debug log
    return taskArray;
  } catch (error) {
    console.error("Error fetching tasks:", error);
    return []; // Return empty array instead of throwing error
  }
}

// Function to add a new task
async function addTask(task) {
  try {
    const taskData = {
      ...task,
      user_id: sessionStorage.getItem("user_id"),
      completed: false,
      timestamp: getCurrentTimestamp(),
    };

    const response = await fetch(API.tasks, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || "Failed to add task");
    }

    const newTask = await response.json();
    console.log("Added task:", newTask); // Debug log
    return newTask;
  } catch (error) {
    console.error("Error adding task:", error);
    throw error;
  }
}

// Function to update a task
async function updateTask(taskId, task) {
  try {
    const response = await fetch(API.task(taskId), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error updating task:", error);
    throw error;
  }
}

// Function to delete a task
async function deleteTask(taskId) {
  try {
    console.log("Deleting task:", taskId); // Debug log
    const response = await fetch(API.task(taskId), {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Delete response:", result); // Debug log
    return result;
  } catch (error) {
    console.error("Error deleting task:", error);
    throw error;
  }
}

// Function to format date to YYYY-MM-DD
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Function to format time to HH:MM
function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("vi-VN", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Ho_Chi_Minh",
  });
}

// Function to get current timestamp in milliseconds
function getCurrentTimestamp() {
  return Date.now();
}

// Function to get current date in Vietnam timezone
function getCurrentVietnamDate() {
  const now = new Date();
  const vietnamTime = new Date(
    now.toLocaleString("en-US", { timeZone: "Asia/Ho_Chi_Minh" })
  );
  return vietnamTime;
}

// Function to get start of week (Monday)
function getStartOfWeek(date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
  return new Date(d.setDate(diff));
}

// Function to get end of week (Sunday)
function getEndOfWeek(date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() + (7 - day); // Adjust when day is Sunday
  return new Date(d.setDate(diff));
}

// Function to format date to readable format
function formatReadableDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  if (date.toDateString() === today.toDateString()) {
    return "Today";
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return "Tomorrow";
  } else {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  }
}

// Function to group tasks by date
function groupTasksByDate(tasks) {
  const grouped = {};
  tasks.forEach((task) => {
    const date = task.date;
    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(task);
  });
  return grouped;
}

// Function to display tasks
async function displayTasks(section) {
  try {
    currentSection = section;
    const tasks = await fetchTasks();
    console.log("Tasks to display:", tasks);
    const todayDate = formatDate(new Date());

    // Filter tasks based on the selected section
    let filteredTasks = tasks.filter((task) => {
      const taskDate = new Date(task.date);
      const taskDateStr = formatDate(taskDate);

      switch (section) {
        case "myDay":
          document.getElementById("header_title").textContent = "My Day";
          return taskDateStr === todayDate;

        case "thisWeek":
          document.getElementById("header_title").textContent = "This Week";
          const today = new Date();
          const startOfWeek = getStartOfWeek(today);
          startOfWeek.setHours(0, 0, 0, 0);
          const endOfWeek = getEndOfWeek(today);
          endOfWeek.setHours(23, 59, 59, 999);
          return taskDate >= startOfWeek && taskDate <= endOfWeek;

        case "thisMonth":
          document.getElementById("header_title").textContent = "This Month";
          const currentMonth = new Date().getMonth();
          const currentYear = new Date().getFullYear();
          const startOfMonth = new Date(currentYear, currentMonth, 1);
          const endOfMonth = new Date(
            currentYear,
            currentMonth + 1,
            0,
            23,
            59,
            59,
            999
          );
          return taskDate >= startOfMonth && taskDate <= endOfMonth;

        case "other":
          document.getElementById("header_title").textContent = "All Tasks";
          return true;

        default:
          return false;
      }
    });

    const taskContainer = document.getElementById("TaskContainer");
    if (!taskContainer) {
      console.error("TaskContainer element not found!");
      return;
    }

    if (filteredTasks.length === 0) {
      taskContainer.innerHTML = '<div class="no-tasks">No tasks found</div>';
      return;
    }

    // Sort tasks by date
    filteredTasks.sort((a, b) => new Date(a.date) - new Date(b.date));

    // Group tasks by date
    const groupedTasks = groupTasksByDate(filteredTasks);

    // Create HTML for each date group
    let html = "";
    Object.keys(groupedTasks)
      .sort()
      .forEach((date) => {
        const tasksForDate = groupedTasks[date];
        const readableDate = formatReadableDate(date);

        html += `
          <div class="date-group">
            <h3 class="date-header">${readableDate}</h3>
            ${tasksForDate
              .map(
                (task) => `
                <div class="card align" data-task-id="${task.id}" data-date="${
                  task.date
                }">
                  <input type="checkbox" name="task" id="${task.id}" ${
                  task.completed ? "checked" : ""
                }>
                  <div class="marker ${task.completed ? "done" : ""}">
                    <span>${task.text}</span>
                  </div>
                  <i class="bx bx-trash-alt delete-task"></i>
                </div>
              `
              )
              .join("")}
          </div>
        `;
      });

    taskContainer.innerHTML = html;

    // Remove existing event listeners
    const newTaskContainer = taskContainer.cloneNode(true);
    taskContainer.parentNode.replaceChild(newTaskContainer, taskContainer);

    // Add event listeners for task interactions
    newTaskContainer.addEventListener("click", async (event) => {
      // Handle checkbox change
      if (event.target.type === "checkbox" && event.target.name === "task") {
        const taskId = event.target.id;
        const taskCard = event.target.closest(".card");
        const taskText = taskCard.querySelector(".marker span").textContent;
        let taskDate = taskCard.getAttribute("data-date");
        if (!taskDate) {
          const tasks = await fetchTasks();
          const found = tasks.find((t) => t.id === taskId);
          taskDate = found ? found.date : "";
        }
        const task = {
          id: taskId,
          text: taskText,
          completed: event.target.checked,
          date: taskDate,
          user_id: sessionStorage.getItem("user_id"),
        };
        try {
          await updateTask(taskId, task);
          const marker = event.target.nextElementSibling;
          if (marker.classList.contains("marker")) {
            marker.classList.toggle("done", task.completed);
          }
        } catch (error) {
          console.error("Error updating task:", error);
          swal({
            title: "Success!",
            text: "Updated",
            icon: "success",
            timer: 1500,
            buttons: false,
          });
        }
      }

      // Handle delete button click
      if (event.target.classList.contains("delete-task")) {
        const taskCard = event.target.closest(".card");
        const taskId = taskCard.dataset.taskId;
        console.log("Delete button clicked for task:", taskId); // Debug log

        try {
          await deleteTask(taskId);
          taskCard.remove();

          // If no tasks left in the container, show "No tasks found"
          if (newTaskContainer.children.length === 0) {
            newTaskContainer.innerHTML =
              '<div class="no-tasks">No tasks found</div>';
          }

          swal({
            title: "Success!",
            text: "Task deleted successfully",
            icon: "success",
            timer: 1500,
            buttons: false,
          });
        } catch (error) {
          console.error("Error deleting task:", error);
          swal({
            title: "Error!",
            text: "Failed to delete task. Please try again.",
            icon: "error",
            timer: 2000,
            buttons: false,
          });
        }
      }
    });
  } catch (error) {
    console.error("Error displaying tasks:", error);
    swal({
      title: "Error!",
      text: "Failed to load tasks. Please refresh the page.",
      icon: "error",
      timer: 2000,
      buttons: false,
    });
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  const todoInput = document.getElementById("todo");
  const dueDateInput = document.getElementById("duedate");
  const myDayLink = document.getElementById("o1");
  const thisWeekLink = document.getElementById("o2");
  const thisMonthLink = document.getElementById("o3");
  const otherLink = document.getElementById("o4");
  const searchInput = document.getElementById("search");
  const burgerIcon = document.getElementById("burgerIcon");
  const containerLeft = document.getElementById("containerLeft");

  // Function to toggle date input visibility
  function toggleDateInput(section) {
    if (dueDateInput) {
      if (section === "myDay") {
        dueDateInput.style.display = "none";
      } else {
        dueDateInput.style.display = "block";
      }
    }
  }

  // Set initial date to today
  if (dueDateInput) {
    const vietnamTime = getCurrentVietnamDate();
    dueDateInput.valueAsDate = vietnamTime;
    dueDateInput.min = formatDate(vietnamTime);
  }

  // Function to handle task submission
  async function handleTaskSubmit() {
    if (!todoInput || !dueDateInput) {
      console.error("Input elements not found!");
      swal({
        title: "Error!",
        text: "System error. Please refresh the page.",
        icon: "error",
        timer: 2000,
        buttons: false,
      });
      return;
    }

    const taskText = todoInput.value.trim();
    let dueDate;

    // If in My Day section, use current date
    if (currentSection === "myDay") {
      dueDate = formatDate(new Date());
    } else {
      dueDate = dueDateInput.value;
    }

    if (taskText === "") {
      swal({
        title: "Error",
        text: "Please enter task description!",
        icon: "error",
        timer: 2000,
        buttons: false,
      });
      return;
    }

    if (!dueDate) {
      swal({
        title: "Error",
        text: "Please select a due date!",
        icon: "error",
        timer: 2000,
        buttons: false,
      });
      return;
    }

    try {
      const task = {
        text: taskText,
        date: dueDate,
        completed: false,
        timestamp: getCurrentTimestamp(),
      };

      await addTask(task);

      // Clear inputs
      todoInput.value = "";
      // Don't reset the date input after adding a task
      // dueDateInput.valueAsDate = getCurrentVietnamDate();

      // Refresh task display
      await displayTasks(currentSection);

      // Show success message
      swal({
        title: "Success!",
        text: "Task added successfully!",
        icon: "success",
        timer: 1500,
        buttons: false,
      });
    } catch (error) {
      console.error("Error adding task:", error);
      swal({
        title: "Error",
        text: error.message || "Failed to add task!",
        icon: "error",
        timer: 2000,
        buttons: false,
      });
    }
  }

  // Add event listeners for task submission
  if (todoInput) {
    todoInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        handleTaskSubmit();
      }
    });
  }

  // Add event listener for plus button
  const plusButton = document.querySelector(".bx-plus");
  if (plusButton) {
    plusButton.addEventListener("click", handleTaskSubmit);
  }

  // Add event listener for date input
  if (dueDateInput) {
    dueDateInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        handleTaskSubmit();
      }
    });
  }

  // Section navigation with active state
  function setActiveLink(activeLink) {
    [myDayLink, thisWeekLink, thisMonthLink, otherLink].forEach((link) => {
      if (link) {
        link.classList.remove("active");
      }
    });
    if (activeLink) {
      activeLink.classList.add("active");
    }
  }

  // Add click event listeners for menu items
  if (myDayLink) {
    myDayLink.addEventListener("click", async (e) => {
      e.preventDefault();
      setActiveLink(myDayLink);
      toggleDateInput("myDay");
      await displayTasks("myDay");
    });
  }

  if (thisWeekLink) {
    thisWeekLink.addEventListener("click", async (e) => {
      e.preventDefault();
      setActiveLink(thisWeekLink);
      toggleDateInput("thisWeek");
      await displayTasks("thisWeek");
    });
  }

  if (thisMonthLink) {
    thisMonthLink.addEventListener("click", async (e) => {
      e.preventDefault();
      setActiveLink(thisMonthLink);
      toggleDateInput("thisMonth");
      await displayTasks("thisMonth");
    });
  }

  if (otherLink) {
    otherLink.addEventListener("click", async (e) => {
      e.preventDefault();
      setActiveLink(otherLink);
      toggleDateInput("other");
      await displayTasks("other");
    });
  }

  // Search functionality
  if (searchInput) {
    searchInput.addEventListener("input", async (event) => {
      const searchText = event.target.value.trim().toLowerCase();
      if (searchText === "") {
        await displayTasks(currentSection);
        return;
      }

      try {
        console.log("Fetching tasks for search...");
        const tasks = await fetchTasks();
        console.log("Tasks fetched.");

        console.log("Filtering tasks...");
        const filteredTasks = tasks.filter((task) =>
          task.text.toLowerCase().includes(searchText)
        );
        console.log("Tasks filtered.");

        const taskContainer = document.getElementById("TaskContainer");
        if (!taskContainer) {
          console.error("TaskContainer element not found!");
          // Don't return here, still try to update if filteredTasks > 0
        }

        if (filteredTasks.length === 0) {
          if (taskContainer) {
            taskContainer.innerHTML =
              '<div class="no-tasks">No matching tasks found</div>';
          }
          return;
        }

        console.log("Grouping tasks...");
        // Group and display filtered tasks
        const groupedTasks = groupTasksByDate(filteredTasks);
        console.log("Tasks grouped.");

        let html = "";
        Object.keys(groupedTasks)
          .sort()
          .forEach((date) => {
            const tasksForDate = groupedTasks[date];
            const readableDate = formatReadableDate(date);

            html += `
            <div class="date-group">
              <h3 class="date-header">${readableDate}</h3>
              ${tasksForDate
                .map(
                  (task) => `
                <div class="card align" data-task-id="${task.id}" data-date="${
                    task.date
                  }">
                  <input type="checkbox" name="task" id="${task.id}" ${
                    task.completed ? "checked" : ""
                  }>
                  <div ${
                    task.completed ? 'class="marker done"' : 'class="marker"'
                  } >
                    <span>${task.text}</span>
                  </div>
                  <i class="bx bx-trash-alt delete-task"></i>
                </div>
              `
                )
                .join("")}
            </div>
          `;
          });

        console.log("Setting innerHTML...");
        if (taskContainer) {
          taskContainer.innerHTML = html;
        }
        console.log("innerHTML set.");

        console.log("Removing time from search results...");
        // Remove time from search results
        if (taskContainer) {
          const taskCards = taskContainer.querySelectorAll(".card");
          taskCards.forEach((card) => {
            const taskTime = card.querySelector(".task-time");
            if (taskTime) {
              taskTime.remove();
            }
          });
        }
        console.log("Time removed.");

        console.log("Re-adding event listeners...");
        // Re-add event listeners for filtered tasks (checkbox and delete)
        // Need to re-get the container after setting innerHTML
        const updatedTaskContainer = document.getElementById("TaskContainer");
        if (updatedTaskContainer) {
          updatedTaskContainer.addEventListener("click", async (event) => {
            // Handle checkbox change
            if (
              event.target.type === "checkbox" &&
              event.target.name === "task"
            ) {
              const taskId = event.target.id;
              const taskCard = event.target.closest(".card");
              const taskText =
                taskCard.querySelector(".marker span").textContent;
              let taskDate = taskCard.getAttribute("data-date");
              if (!taskDate) {
                const tasks = await fetchTasks();
                const found = tasks.find((t) => t.id === taskId);
                taskDate = found ? found.date : "";
              }
              const task = {
                id: taskId,
                text: taskText,
                completed: event.target.checked,
                date: taskDate,
                user_id: sessionStorage.getItem("user_id"),
              };
              try {
                await updateTask(taskId, task);
                const marker = event.target.nextElementSibling;
                if (marker.classList.contains("marker")) {
                  marker.classList.toggle("done", task.completed);
                }
              } catch (error) {
                console.error("Error updating task:", error);
                swal({
                  title: "Success!",
                  text: "Updated",
                  icon: "success",
                  timer: 1500,
                  buttons: false,
                });
              }
            }

            // Handle delete button click
            if (event.target.classList.contains("delete-task")) {
              const taskCard = event.target.closest(".card");
              const taskId = taskCard.dataset.taskId;
              console.log("Delete button clicked for task:", taskId); // Debug log

              try {
                await deleteTask(taskId);
                taskCard.remove();

                // If no tasks left in the container, show "No tasks found"
                if (updatedTaskContainer.children.length === 0) {
                  updatedTaskContainer.innerHTML =
                    '<div class="no-tasks">No tasks found</div>';
                }

                swal({
                  title: "Success!",
                  text: "Task deleted successfully",
                  icon: "success",
                  timer: 1500,
                  buttons: false,
                });
              } catch (error) {
                console.error("Error deleting task:", error);
                swal({
                  title: "Error!",
                  text: "Failed to delete task. Please try again.",
                  icon: "error",
                  timer: 2000,
                  buttons: false,
                });
              }
            }
          });
        }
        console.log("Event listeners re-added.");
      } catch (error) {
        console.error("Error searching tasks:", error);
        swal({
          title: "Error!",
          text: "Failed to search tasks. Please try again.",
          icon: "error",
          timer: 2000,
          buttons: false,
        });
      }
    });
  }

  // Mobile menu toggle
  if (burgerIcon && containerLeft) {
    burgerIcon.addEventListener("click", () => {
      burgerIcon.classList.toggle("active");
      containerLeft.classList.toggle("active");
    });
  }

  // Set initial active link and display tasks
  if (myDayLink) {
    setActiveLink(myDayLink);
    toggleDateInput("myDay");
    displayTasks("myDay");
  }
});
