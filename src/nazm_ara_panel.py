from widgets import PushButton, RadioButton

from PySide6.QtCore import (
    Qt,
    QMargins,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget,
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
        self.content_area = MainSection()
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

    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        self.todo_page = QLabel("Todo List")   # TODO: task list class
        self.habit_page = QLabel("Habit List") # TODO: habit list class

        # Add pages to stack
        self.pages.addWidget(self.choose_one)
        self.pages.addWidget(self.todo_page)
        self.pages.addWidget(self.habit_page)
        
        self.layout.addWidget(self.pages)

        self.todo_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.TODO_PAGE))
        self.habit_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.HABIT_PAGE))
