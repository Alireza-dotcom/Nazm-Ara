from widgets import PushButton, RadioButton, TodoListItemWidget, TodoCalendar
from modals import AddTodoModal
from notification_handler import NotificationHandler
from database_manager import DatabaseManager

from PySide6.QtCore import (
    Qt,
    QMargins,
    QDate,
    QPoint
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem
)

class NazmAra(QWidget):
    SPACING_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent, account_details):
        super().__init__(parent)
        self.setObjectName("NazmAra")
        self.account_details = account_details
        
        # Main Horizontal Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(NazmAra.CONTENTS_MARGINS_SIZE)
        self.main_layout.setSpacing(NazmAra.SPACING_SIZE)

        # Instantiate Sub-classes
        self.sidebar = UserControlSidebar()
        self.content_area = MainSection(self, self.account_details)
        self.content_area.setObjectName("MainSection")

        # Add to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area, NazmAra.SPACING_SIZE)


class UserControlSidebar(QFrame):
    STRETCH_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(10, 10, 10, 10)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60)
        self.setObjectName("Sidebar")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UserControlSidebar.CONTENTS_MARGINS_SIZE)
        layout.setAlignment(Qt.AlignTop)

        # Initialize Buttons
        self.profile_button = PushButton(self)
        self.profile_button.setIcon(QIcon(":icons/profile.svg"))
        
        self.save_button = PushButton(self)
        self.save_button.setIcon(QIcon(":icons/upload.svg"))
        
        self.settings_button = PushButton(self)
        self.settings_button.setIcon(QIcon(":icons/settings.svg"))

        # Add to layout
        layout.addWidget(self.profile_button)
        layout.addStretch(UserControlSidebar.STRETCH_SIZE)
        layout.addWidget(self.save_button)
        layout.addWidget(self.settings_button)


class MainSection(QFrame):
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)
    TODO_PAGE  = 1
    HABIT_PAGE = 2

    def __init__(self, parent=None, account_details=None):
        super().__init__(parent)
        self.account_details = account_details

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(MainSection.CONTENTS_MARGINS_SIZE)

        # Upper Navigation Frame
        self.upper_frame = QFrame()
        self.upper_frame.setObjectName("UpperFrame")
        upper_layout = QHBoxLayout(self.upper_frame)

        self.todo_list_btn = RadioButton("Todo list", self)
        self.habit_list_btn = RadioButton("Habit list", self)

        upper_layout.addWidget(self.todo_list_btn)
        upper_layout.addWidget(self.habit_list_btn)

        self.layout.addWidget(self.upper_frame)

        self.pages = QStackedWidget()

        self.choose_one = QLabel("choose one")
        self.todo_page = TodoWidget(self, self.account_details)
        self.habit_page = QLabel("Habit List") # TODO: habit list class

        # Add pages to stack
        self.pages.addWidget(self.choose_one)
        self.pages.addWidget(self.todo_page)
        self.pages.addWidget(self.habit_page)
        
        self.layout.addWidget(self.pages)

        self.todo_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.TODO_PAGE))
        self.habit_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.HABIT_PAGE))


class TodoWidget(QWidget):
    STRETCH_SIZE = 1

    def __init__(self, parent=None, account_details=None):
        super().__init__(parent)
        self.account_details = account_details
        self.database = DatabaseManager()
        self.notification_handler = NotificationHandler()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header Section
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("AddTodoFrame")
        self.active_date = QDate.currentDate()

        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setAlignment(Qt.AlignLeft)

        self.todo_calendar = TodoCalendar(self.active_date, parent=self)
        self.todo_calendar.day_changed.connect(self.jumpToSelectedDay)

        self.calendar_btn = PushButton(parent=self)
        self.calendar_btn.clicked.connect(self.showCalendarAtButton)
        self.calendar_btn.setIcon(QIcon(":icons/calendar.svg"))

        self.previous_day_btn = PushButton(parent=self)
        self.previous_day_btn.setIcon(QIcon(":icons/previous_day.svg"))
        self.previous_day_btn.clicked.connect(lambda: self.nextAndPreviousDay(-1))

        self.date_label = QLabel("Today", self)
        self.date_label.setFixedWidth(165)
        self.date_label.setAlignment(Qt.AlignCenter)

        self.next_day_btn = PushButton(parent=self)
        self.next_day_btn.setIcon(QIcon(":icons/next_day.svg"))
        self.next_day_btn.clicked.connect(lambda: self.nextAndPreviousDay(1))

        self.go_to_today_btn = PushButton("Today", self)
        self.go_to_today_btn.clicked.connect(self.jumpToToday)

        self.add_task_btn = PushButton("+ Add task", self)
        self.add_task_btn.setObjectName("AddTaskBtn")
        self.add_task_btn.clicked.connect(self.showModal)

        self.header_layout.addWidget(self.calendar_btn)
        self.header_layout.addWidget(self.previous_day_btn)
        self.header_layout.addWidget(self.date_label)
        self.header_layout.addWidget(self.next_day_btn)
        self.header_layout.addWidget(self.go_to_today_btn)
        
        self.header_layout.addStretch(TodoWidget.STRETCH_SIZE)
        self.header_layout.addWidget(self.add_task_btn)
        self.main_layout.addWidget(self.header_frame)

        # Accounts list
        self.list_widget = QListWidget(self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.main_layout.addWidget(self.list_widget)

        self.loadTasks()


    def showCalendarAtButton(self):
        button_pos = self.calendar_btn.mapToGlobal(QPoint(0, 0))
        
        calendar_pos = button_pos + QPoint(0, self.calendar_btn.height())
        
        self.todo_calendar.setSelectedDate(self.active_date)
        self.todo_calendar.move(calendar_pos)
        self.todo_calendar.show()


    def jumpToSelectedDay(self, date):
        current_day = self.active_date
        self.nextAndPreviousDay(current_day.daysTo(date))


    def loadTasks(self):
        date_string = self.active_date.toString(Qt.ISODate)
        tasks = self.database.getTasksByDate(date_string, self.account_details["id"])

        for row in tasks:
            item = QListWidgetItem(self.list_widget)
            custom_widget = TodoListItemWidget(row, self)
            custom_widget.on_check_button_clicked.connect(self.checkedOrUncheckedTask)
            item.setSizeHint(custom_widget.sizeHint())
            item.setData(Qt.UserRole, row)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def checkedOrUncheckedTask(self, task_object, task_id, value):
        status = self.database.toggleTask(task_id, value)
        if status:
            task_object.toggleCheckedBtn()
        else:
            task_object.check_btn.setChecked(False)
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def showModal(self):
        self.modal = AddTodoModal(self)
        self.modal.add_todo_clicked.connect(self.createTodo)


    def createTodo(self, details):
        details["date_time"] = self.active_date.toString(Qt.ISODate)
        user_id = self.account_details["id"]
        task_id = self.database.addTask(details["title"], user_id ,details["description"],
                                details["priority"], details["date_time"])
        if task_id:
            details["local_id"] = task_id

            item = QListWidgetItem(self.list_widget)
            custom_widget = TodoListItemWidget(details, self)
            custom_widget.on_check_button_clicked.connect(self.checkedOrUncheckedTask)
            item.setSizeHint(custom_widget.sizeHint())
            item.setData(Qt.UserRole, details)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def nextAndPreviousDay(self, next_or_previous):
        curent_day = QDate.currentDate()
        self.active_date = self.active_date.addDays(next_or_previous)
        diff = curent_day.daysTo(self.active_date)

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
        self.active_date = QDate.currentDate()
        self.date_label.setText("Today")

        self.list_widget.clear()
        self.loadTasks()
