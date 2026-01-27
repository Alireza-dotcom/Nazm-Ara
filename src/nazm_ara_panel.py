from modals import SettingsModal
from database_manager import DatabaseManager
from notification_handler import NotificationHandler
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
    QPoint,
    Signal
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget,
    QFileDialog
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
        self.sidebar.data_imported_signal.connect(self.dataImported)
        self.content_area = MainSection(account_details=self.account_details, parent=self)
        self.content_area.setObjectName("MainSection")

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area, NazmAra.SPACING_SIZE)


    def dataImported(self):
        self.content_area.task_page.loadTasks()
        self.content_area.habit_page.loadHabits()


class UserControlSidebar(QFrame):
    """Vertical navigation bar for global actions like Profile, Cloud Sync, and Settings."""
    data_imported_signal = Signal()
    STRETCH_SIZE = 1
    CONTENTS_MARGINS_SIZE = QMargins(10, 10, 10, 10)

    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent)
        self.setFixedWidth(60)
        self.setObjectName("Sidebar")
        self.account_details = account_details
        self.online_user = self.account_details.get("user_id")
        self.database = DatabaseManager()
        self.notification_handler = NotificationHandler()
        
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
        self.settings_button.clicked.connect(self.displaySettingsModal)
        layout.addStretch(UserControlSidebar.STRETCH_SIZE)
        layout.addWidget(self.settings_button)


    def displaySettingsModal(self):
        self.modal = SettingsModal(self)
        self.modal.export_btn.clicked.connect(self.exportData)
        self.modal.import_btn.clicked.connect(self.importData)


    def importData(self):
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open file",
            dir="",
            filter="JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            user_id = self.account_details.get("id")
            if self.database.importUserData(json_file=file_path, new_user_id=user_id):
                self.data_imported_signal.emit()
                self.notification_handler.showToast(
                    "bottom_right", "Import successful",
                    "Your data has been imported successfully", "success", duration=4000
                )
            else:
                self.notification_handler.showToast(
                    "bottom_right", "Couldn't import data",
                    "A temporary error occurred. Please try again.", "error", duration=4000
                )


    def exportData(self):
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save JSON file",
            dir="data.json",
            filter="JSON Files (*.json)"
        )

        if file_path:
            if not file_path.lower().endswith(".json"):
                file_path += ".json"

            user_id = self.account_details.get("id")
            if self.database.exportUserData(output_file=file_path, user_id=user_id):
                self.notification_handler.showToast(
                    "bottom_right", "Export successful",
                    "Your data has been exported successfully", "success", duration=4000
                )
            else:
                self.notification_handler.showToast(
                    "bottom_right", "Couldn't export data",
                    "A temporary error occurred. Please try again.", "error", duration=4000
                )


    def showAccountDetails(self):
        button_pos = self.profile_button.mapToGlobal(QPoint(0, 0))
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
    HABIT_DETAILS_PAGE_INDEX = 3

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

        self.pages = QStackedWidget(parent=self)
        self.pages.currentChanged.connect(self.removeHabitDetailsPageOnExit)

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


    def removeHabitDetailsPageOnExit(self):
        if self.pages.count() == 4 and \
        not self.pages.currentIndex() == MainSection.HABIT_DETAILS_PAGE_INDEX:
            self.pages.widget(MainSection.HABIT_DETAILS_PAGE_INDEX).deleteLater()
            self.habit_page.resetHabits()


    def displayTaskList(self):
        main_window = self.window()
        main_window.style_sheet_handler.setResourceQssPath(":/styles/task_widget.qss")
        self.pages.setCurrentIndex(MainSection.TASK_PAGE_INDEX)


    def displayHabitList(self):
        main_window = self.window()
        main_window.style_sheet_handler.setResourceQssPath(":/styles/habit_widget.qss")
        self.pages.setCurrentIndex(MainSection.HABIT_PAGE_INDEX)
