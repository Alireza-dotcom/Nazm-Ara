import sys
from login_panel import LoginPanel
from forgot_password_panel import ForgotPasswordPanel
from signup_panel import SignupPanel
from offline_user_panel import OfflineUserPanel
from utils import loadFont
from style_sheet_handler import StyleSheetHandler
from select_acc_panel import SelectAccountPanel
from database_manager import DatabaseManager
from nazm_ara_panel import NazmAra
from notification_handler import NotificationHandler
import resources_rc

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QMainWindow,
    QHBoxLayout,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")

        self.latin_font_family = loadFont(":fonts/Nunito.ttf")
        self.persian_font_family = loadFont(":fonts/Vazirmatn.ttf")

        self.database = DatabaseManager()
        self.style_sheet_handler = StyleSheetHandler(self)
        self.notification_handler = NotificationHandler(self)

        self.setMinimumSize(1024, 768)
        self.resize(1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.stack)


        if self.database.getListOfUsers():
            self.showSelectAccountPage()
        else:
            self.showLoginPage()


    def showLoginPage(self):
        self.style_sheet_handler.setResourceQssPath(":/styles/login_panel.qss")
        self.login_panel = self.loadPage(LoginPanel)
        self.login_panel.forgot_clicked.connect(self.showForgotPasswordPage)
        self.login_panel.signup_clicked.connect(self.showSignupPage)
        self.login_panel.select_account_clicked.connect(self.showSelectAccountPage)
        self.login_panel.continue_clicked.connect(self.showOfflineAccountPanel)
        self.login_panel.login_clicked.connect(self.logIntoOnlineAccount)
        self.shrinkPage()
        self.addSpacing()


    def showSelectAccountPage(self):
        self.style_sheet_handler.setResourceQssPath(":/styles/select_acc_panel.qss")
        self.select_account_panel = self.loadPage(SelectAccountPanel)
        self.select_account_panel.add_account_clicked.connect(self.showLoginPage)
        self.select_account_panel.account_selected.connect(self.openMainApp)
        self.shrinkPage()
        self.addSpacing()


    def showOfflineAccountPanel(self):
        self.style_sheet_handler.setResourceQssPath(":/styles/offline_acc_panel.qss")
        self.offline_account_panel = self.loadPage(OfflineUserPanel)
        self.offline_account_panel.back_to_login_clicked.connect(self.showLoginPage)
        self.offline_account_panel.continue_clicked.connect(self.createOfflineUser)


    def openMainApp(self, account_row: dict):
        self.style_sheet_handler.setResourceQssPath(":/styles/nazm_ara_panel.qss")
        self.loadPage(NazmAra, account_row)
        self.resetShrinkPage()
        self.removeSpacing()


    def showForgotPasswordPage(self):
        self.style_sheet_handler.setResourceQssPath(":/styles/forgot_pass_panel.qss")
        self.forgot_pass_panel = self.loadPage(ForgotPasswordPanel)
        self.forgot_pass_panel.back_to_login_clicked.connect(self.showLoginPage)
        self.forgot_pass_panel.create_new_acc_clicked.connect(self.showSignupPage)
        self.forgot_pass_panel.reset_password_clicked.connect(self.sendResetPassEmail)


    def showSignupPage(self):
        self.style_sheet_handler.setResourceQssPath(":/styles/signup_panel.qss")
        self.signup_panel = self.loadPage(SignupPanel)
        self.signup_panel.already_have_account_clicked.connect(self.showLoginPage)
        self.signup_panel.signup_clicked.connect(self.createOnlineUser)


    def loadPage(self, ClassWidget, *args, **kwargs):
        previous_widget = self.stack.currentWidget()

        new_widget = ClassWidget(self, *args, **kwargs)
        index = self.stack.addWidget(new_widget)

        self.stack.setCurrentIndex(index)
        if previous_widget:
            self.stack.removeWidget(previous_widget)
            previous_widget.deleteLater()
        
        return new_widget


    def resizeEvent(self, event):
        self.shrinkPage()
        self.style_sheet_handler.updateStylesheet()

        super().resizeEvent(event)

    def shrinkPage(self):
        if not self.stack.currentWidget().objectName() == "NazmAra":
            MIN_PANEL_WIDTH = 430
            PANEL_WIDTH_RATIO = 0.32

            window_width = self.width()
            target_width = max(MIN_PANEL_WIDTH, int(window_width * PANEL_WIDTH_RATIO)) # 32% of width, min 430px
            self.stack.setFixedWidth(target_width)


    def resetShrinkPage(self):
        self.stack.setMinimumWidth(0)
        self.stack.setMaximumWidth(16777215)


    def addSpacing(self):
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(9, 9, 9, 9)


    def removeSpacing(self):
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)


    def createOfflineUser(self, data):
        if self.database.addOfflineUser(data['nickname'], data['first_name'], data['last_name']):
            self.notification_handler.showToast(
                "bottom_right", "Welcome!",
                "Your account has been successfully created.", "success", duration=4000
            )
            user_info = self.database.getListOfUsers()[-1]
            self.openMainApp(user_info)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn’t Create Account",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )



    def logIntoOnlineAccount(self):
        #TODO: add login functionality
        pass


    def sendResetPassEmail(self, email):
        # TODO: add reset password
        pass


    def createOnlineUser(self, data):
        # TODO: add online user creation
        pass


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Nazm Ara")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
