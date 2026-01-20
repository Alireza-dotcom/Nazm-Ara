from widgets import PushButton, RadioButton
from habbit_list import HabitWidget
from task_list import TaskWidget

from PySide6.QtCore import (
    Qt,
    QMargins
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget
)

class NazmAra(QWidget):
    """The primary application container after login."""
    SPACING_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent, account_details: dict):
        super().__init__(parent)
        self.setObjectName("NazmAra")
        self.account_details = account_details
        
        # Horizontal layout to place Sidebar next to Content
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(NazmAra.CONTENTS_MARGINS_SIZE)
        self.main_layout.setSpacing(NazmAra.SPACING_SIZE)

        # Component Initialization
        self.sidebar = UserControlSidebar()
        self.content_area = MainSection(self, self.account_details)
        self.content_area.setObjectName("MainSection")

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area, NazmAra.SPACING_SIZE)


class UserControlSidebar(QFrame):
    """Vertical navigation bar for global actions like Profile, Cloud Sync, and Settings."""
    STRETCH_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(10, 10, 10, 10)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60)
        self.setObjectName("Sidebar")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UserControlSidebar.CONTENTS_MARGINS_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.profile_button = PushButton(parent=self)
        self.profile_button.clicked.connect(self.logOutOfAccount)
        self.profile_button.setIcon(QIcon(":icons/profile.svg"))
        
        self.save_button = PushButton(parent=self)
        self.save_button.setIcon(QIcon(":icons/upload.svg"))
        
        self.settings_button = PushButton(parent=self)
        self.settings_button.setIcon(QIcon(":icons/settings.svg"))

        layout.addWidget(self.profile_button)
        layout.addStretch(UserControlSidebar.STRETCH_SIZE)
        layout.addWidget(self.save_button)
        layout.addWidget(self.settings_button)


    def logOutOfAccount(self):
        self.window().showSelectAccountPage()
        RadioButton.resetRadioButtons()



class MainSection(QFrame):
    """
    The central content switcher. 
    Uses a QStackedWidget to transition between the Welcome screen, Task list, and Habit list.
    """
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)
    TODO_PAGE_INDEX  = 1
    HABIT_PAGE_INDEX = 2

    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent)
        self.account_details = account_details

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(MainSection.CONTENTS_MARGINS_SIZE)

        # Top Navigation Frame
        self.upper_frame = QFrame()
        self.upper_frame.setObjectName("UpperFrame")
        upper_layout = QHBoxLayout(self.upper_frame)

        self.task_list_btn = RadioButton(text="Task list", parent=self)
        self.habit_list_btn = RadioButton(text="Habit list", parent=self)

        upper_layout.addWidget(self.task_list_btn)
        upper_layout.addWidget(self.habit_list_btn)
        self.layout.addWidget(self.upper_frame)

        self.pages = QStackedWidget()

        self.welcome_page = QLabel(text=f"Hay {account_details.get("f_name")}!\nChoose a path to get started.",
                                   parent=self, alignment=Qt.AlignmentFlag.AlignCenter
                                  )
        self.welcome_page.setObjectName("WelcomePage")
        self.task_page = TaskWidget(self, self.account_details)
        self.habit_page = HabitWidget(self, self.account_details)

        # Add pages to stack
        self.pages.addWidget(self.welcome_page)
        self.pages.addWidget(self.task_page)
        self.pages.addWidget(self.habit_page)
        
        self.layout.addWidget(self.pages)

        # Page Switching Logic
        self.task_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.TODO_PAGE_INDEX))
        self.habit_list_btn.clicked.connect(lambda: self.pages.setCurrentIndex(MainSection.HABIT_PAGE_INDEX))
