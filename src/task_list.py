from widgets import PushButton, TaskListItemWidget, TaskCalendar
from modals import AddTaskModal
from notification_handler import NotificationHandler
from database_manager import DatabaseManager

from PySide6.QtCore import (
    Qt,
    QDate,
    QPoint,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
)

class TaskWidget(QWidget):
    """task management view."""
    STRETCH_SIZE = 1

    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent)
        self.account_details = account_details
        self.database = DatabaseManager()
        self.notification_handler = NotificationHandler(self)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Calendar & Date Controls Header
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("AddTaskFrame")
        self.active_date = QDate.currentDate()

        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Initialize Calendar Popup
        self.task_calendar = TaskCalendar(self.active_date, parent=self)
        self.task_calendar.day_changed.connect(self.jumpToSelectedDay)
        self.highlightTaskDays()

        # Date Navigation Buttons
        self.calendar_btn = PushButton(parent=self)
        self.calendar_btn.clicked.connect(self.showCalendarAtButton)
        self.calendar_btn.setIcon(QIcon(":icons/calendar.svg"))

        self.previous_day_btn = PushButton(parent=self)
        self.previous_day_btn.setIcon(QIcon(":icons/previous_day.svg"))
        self.previous_day_btn.clicked.connect(lambda: self.nextAndPreviousDay(-1))

        self.date_label = QLabel(text="Today", parent=self)
        self.date_label.setFixedWidth(175)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_day_btn = PushButton(parent=self)
        self.next_day_btn.setIcon(QIcon(":icons/next_day.svg"))
        self.next_day_btn.clicked.connect(lambda: self.nextAndPreviousDay(1))

        self.go_to_today_btn = PushButton(text="Today", parent=self)
        self.go_to_today_btn.clicked.connect(self.jumpToToday)

        self.add_task_btn = PushButton(text="+ Add task", parent=self)
        self.add_task_btn.setObjectName("AddTaskBtn")
        self.add_task_btn.clicked.connect(self.showCreateModal)

        self.header_layout.addWidget(self.calendar_btn)
        self.header_layout.addWidget(self.previous_day_btn)
        self.header_layout.addWidget(self.date_label)
        self.header_layout.addWidget(self.next_day_btn)
        self.header_layout.addWidget(self.go_to_today_btn)
        
        self.header_layout.addStretch(TaskWidget.STRETCH_SIZE)
        self.header_layout.addWidget(self.add_task_btn)
        self.main_layout.addWidget(self.header_frame)

        # Task List Display
        self.list_widget = QListWidget(self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.main_layout.addWidget(self.list_widget)

        # Initial data load
        self.loadTasks()


    def showCalendarAtButton(self):
        """Positions and displays the TaskCalendar popup relative to its trigger button."""
        button_pos = self.calendar_btn.mapToGlobal(QPoint(0, 0))
        calendar_pos = button_pos + QPoint(0, self.calendar_btn.height())
        
        self.task_calendar.setSelectedDate(self.active_date)
        self.task_calendar.move(calendar_pos)
        self.task_calendar.show()


    def jumpToSelectedDay(self, date: QDate):
        """Navigates to a specific date selected from the calendar."""
        current_day = self.active_date
        self.nextAndPreviousDay(current_day.daysTo(date))


    def loadTasks(self):
        """Retrieves tasks for the currently active date from the database and renders them."""
        date_string = self.active_date.toString(Qt.DateFormat.ISODate)
        tasks = self.database.getTasksByDate(date_string, self.account_details.get("id"))

        for row in tasks:
            item = QListWidgetItem(self.list_widget)
            custom_widget = TaskListItemWidget(row, self)
            # Connect signals from custom item widget for task updates
            custom_widget.on_check_button_clicked.connect(self.checkedOrUncheckedTask)
            custom_widget.on_edit_button_clicked.connect(self.showEditModal)

            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def checkedOrUncheckedTask(self, task_item_widget: TaskListItemWidget, task_id: str, value: bool):
        """Updates the completion status of a task in the database."""
        status = self.database.toggleTask(task_id, value)
        if status:
            task_item_widget.toggleCheckedBtn()
        else:
            # Fallback if DB update fails
            task_item_widget.check_btn.setChecked(False)
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def showCreateModal(self):
        """Opens the modal to create a new task."""
        self.modal = AddTaskModal(self, False)
        self.modal.add_task_clicked.connect(self.createTask)


    def showEditModal(self, task_item_widget: TaskListItemWidget, task_details: dict):
        """Opens the modal to edit or delete an existing task."""
        self.modal = AddTaskModal(self, task_item_widget, task_details)
        self.modal.on_update_clicked.connect(self.updateTask)
        self.modal.on_delete_clicked.connect(self.deleteTask)


    def updateTask(self, task_item_widget: TaskListItemWidget, task_details: dict, local_id: str):
        """Validates and saves modifications to an existing task."""
        title = task_details.get("title")
        desc = task_details.get("description")
        priority = task_details.get("priority")
        if self.database.updateTask(local_id, title=title, description=desc, priority=priority):
            task_item_widget.update(priority, desc, title)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def deleteTask(self, task_item_widget: TaskListItemWidget, local_id: str):
        """Removes a task from the database and the UI list."""
        if self.database.deleteTask(local_id):
            item = self.list_widget.itemAt(task_item_widget.pos())
            row = self.list_widget.row(item)
            taken_item = self.list_widget.takeItem(row) # Removes the item from view
            del taken_item

            # Remove calendar highlight if no tasks remain for this date
            if self.list_widget.count() == 0:
                self.task_calendar.clearTaskColor(self.active_date)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def createTask(self, task_details: dict):
        """Adds a new task to the database and add it into the current view."""
        task_details["date_time"] = self.active_date.toString(Qt.DateFormat.ISODate)
        user_id = self.account_details.get("id")
        task_id = self.database.addTask(task_details.get("title"), user_id ,task_details.get("description"),
                                task_details.get("priority"), task_details.get("date_time"))
        if task_id:
            task_details["local_id"] = task_id

            item = QListWidgetItem(self.list_widget)
            custom_widget = TaskListItemWidget(task_details, self)
            custom_widget.on_check_button_clicked.connect(self.checkedOrUncheckedTask)
            custom_widget.on_edit_button_clicked.connect(self.showEditModal)
            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )
        # Update calendar to show this date now has a task
        self.task_calendar.setTaskColor([self.active_date])


    def nextAndPreviousDay(self, next_or_previous: int):
        """Adjusts the active date, updates labels, and reloads the task list."""
        curent_day = QDate.currentDate()
        self.active_date = self.active_date.addDays(next_or_previous)
        diff = curent_day.daysTo(self.active_date)

        # Human-readable date labeling
        if diff == -1:
            self.date_label.setText("Yesterday")
        elif diff == 0:
            self.date_label.setText("Today")
        elif diff == 1:
            self.date_label.setText("Tomorrow")
        else:
            self.date_label.setText(self.active_date.toString(("d-MMMM-yyyy")))
        
        self.list_widget.clear()
        self.loadTasks()


    def jumpToToday(self):
        """Reset the view to the current system date."""
        self.active_date = QDate.currentDate()
        self.date_label.setText("Today")

        self.list_widget.clear()
        self.loadTasks()


    def highlightTaskDays(self):
        """Queries the database for all dates with tasks and applies calendar formatting."""
        dates = self.database.getUserTaskDates(self.account_details.get("id"))
        qdates = [QDate.fromString(date, Qt.DateFormat.ISODate) for date in dates]
        self.task_calendar.setTaskColor(qdates)