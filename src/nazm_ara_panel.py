from widgets import (
    PushButton,
    RadioButton,
    AccountDetailsFrame
)
from habbit_list import HabitWidget
from task_list import TaskWidget
from PySide6.QtCore import (
    Qt,
    QMargins,
    QPoint
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
        self.sidebar = UserControlSidebar(account_details=self.account_details, parent=self)
        self.content_area = MainSection(account_details=self.account_details, parent=self)
        self.content_area.setObjectName("MainSection")

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area, NazmAra.SPACING_SIZE)


class UserControlSidebar(QFrame):
    """Vertical navigation bar for global actions like Profile, Cloud Sync, and Settings."""
    STRETCH_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(10, 10, 10, 10)

    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent)
        self.setFixedWidth(60)
        self.setObjectName("Sidebar")
        self.account_details = account_details
        self.online_user = self.account_details.get("user_id")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UserControlSidebar.CONTENTS_MARGINS_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.profile_details_Frame = AccountDetailsFrame(parent=self, account_details=account_details)
        self.profile_details_Frame.logout_btn.clicked.connect(self.logOutOfAccount)
        self.profile_button = PushButton(parent=self)
        self.profile_button.clicked.connect(self.showAccountDetails)
        self.profile_button.setIcon(QIcon(":icons/profile.svg"))
        layout.addWidget(self.profile_button)

        if self.online_user:
            self.save_button = PushButton(parent=self)
            self.save_button.setIcon(QIcon(":icons/upload.svg"))
            layout.addWidget(self.save_button)
        
        self.settings_button = PushButton(parent=self)
        self.settings_button.setIcon(QIcon(":icons/settings.svg"))
        layout.addStretch(UserControlSidebar.STRETCH_SIZE)
        layout.addWidget(self.settings_button)


    def showAccountDetails(self):
        button_pos = self.profile_button.mapToGlobal(QPoint(0, 0))
        print(button_pos)
        frame_pos = button_pos + QPoint(0, self.profile_button.height())
        
        self.profile_details_Frame.move(frame_pos)
        self.profile_details_Frame.show()


    def logOutOfAccount(self):
        self.window().showSelectAccountPage()
        RadioButton.resetRadioButtons()


class MainSection(QFrame):
    """
    The central content switcher. 
    Uses a QStackedWidget to transition between the Welcome screen, Task list, and Habit list.
    """
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)
    TASK_PAGE_INDEX  = 1
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
        self.task_list_btn.clicked.connect(self.displayTaskList)
        self.habit_list_btn.clicked.connect(self.displayHabitList)


    def displayTaskList(self):
        main_window = self.window()
        main_window.style_sheet_handler.setResourceQssPath(":/styles/task_widget.qss")
        self.pages.setCurrentIndex(MainSection.TASK_PAGE_INDEX)


    def displayHabitList(self):
        main_window = self.window()
        main_window.style_sheet_handler.setResourceQssPath(":/styles/habit_widget.qss")
        self.pages.setCurrentIndex(MainSection.HABIT_PAGE_INDEX)
