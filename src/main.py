import sys
from login_panel import LoginPanel
from forgot_password_panel import ForgotPasswordPanel
from signup_panel import SignupPanel
from utils import loadStylesheet
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
        loadStylesheet(self, ":styles/login.qss")

        self.setMinimumSize(1024, 768)
        self.resize(1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()

        self.showLoginPage()

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.stack)


    def showLoginPage(self):
        self.login_panel = self.loadPage(LoginPanel)
        self.login_panel.forgot_clicked.connect(self.showForgotPasswordPage)
        self.login_panel.signup_clicked.connect(self.showSignupPage)


    def showForgotPasswordPage(self):
        self.forgot_pass_panel = self.loadPage(ForgotPasswordPanel)
        self.forgot_pass_panel.back_to_login_clicked.connect(self.showLoginPage)
        self.forgot_pass_panel.create_new_acc_clicked.connect(self.showSignupPage)


    def showSignupPage(self):
        self.signup_panel = self.loadPage(SignupPanel)
        self.signup_panel.already_have_account_clicked.connect(self.showLoginPage)


    def loadPage(self, ClassWidget):
        previous_widget = self.stack.currentWidget()

        new_widget = ClassWidget(self)
        index = self.stack.addWidget(new_widget)

        self.stack.setCurrentIndex(index)
        if previous_widget:
            self.stack.removeWidget(previous_widget)
            previous_widget.deleteLater()
        
        return new_widget


    def resizeEvent(self, event):
        MIN_PANEL_WIDTH = 430
        PANEL_WIDTH_RATIO = 0.32

        window_width = self.width()
        target_width = max(MIN_PANEL_WIDTH, int(window_width * PANEL_WIDTH_RATIO)) # 32% of width, min 430px
        self.stack.setFixedWidth(target_width)

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Nazm Ara")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
