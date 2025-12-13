from widgets import PasswordField, ClickableLabel, PushButton

from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Qt,
    Signal,
    QMargins,
    QSize
)
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QLineEdit,
    QVBoxLayout,
)


class LoginPanel(QFrame):
    forgot_clicked = Signal()
    signup_clicked = Signal()
    continue_clicked = Signal()

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    LOGO_SIZE = QSize(250, 250)
    CONTENTS_MARGIN_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("LoginPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(LoginPanel.CONTENTS_MARGIN_SIZE)
        layout.setSpacing(LoginPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap("../res/logos/logo.png")
        logo_file = logo_file.scaled(LoginPanel.LOGO_SIZE)
        logo.setPixmap(QPixmap(logo_file))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        # Title
        title = QLabel("Login", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Email field
        email_label = QLabel("Email", self)
        email_label.setObjectName("FieldLabel")
        layout.addWidget(email_label)

        self.email_input = QLineEdit(self)
        self.email_input.setObjectName("FieldLabel")
        layout.addWidget(self.email_input)

        # Password field
        password_label = QLabel("Password", self)
        password_label.setObjectName("FieldLabel")
        layout.addWidget(password_label)

        self.password_input = PasswordField(self)
        self.password_input.setObjectName("PasswordInput")
        layout.addWidget(self.password_input)

        # Forgot password link
        forgot_label = ClickableLabel("Forgot your password?", self)
        forgot_label.clicked.connect(self.onForgotClicked)
        forgot_label.setObjectName("FieldLabel")
        forgot_label.setAlignment(Qt.AlignRight)
        layout.addWidget(forgot_label)

        # Login button
        login_btn = PushButton("Login", self)
        layout.addWidget(login_btn)

        # Divider
        divider = QLabel("──────────  or continue offline  ──────────", self)
        divider.setAlignment(Qt.AlignCenter)
        divider.setObjectName("DividerLabel")
        layout.addWidget(divider)

        # Continue button
        self.cont_btn = PushButton("Continue without Account", self)
        layout.addWidget(self.cont_btn)
        self.cont_btn.clicked.connect(self.onCntClicked)

        # Signup text
        signup_label = ClickableLabel("Don't have an account? Sign up", self)
        signup_label.clicked.connect(self.onSignupClicked)
        signup_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(signup_label)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

    def onForgotClicked(self):
        self.forgot_clicked.emit()

    def onSignupClicked(self):
        self.signup_clicked.emit()

    def onCntClicked(self):
        self.continue_clicked.emit()