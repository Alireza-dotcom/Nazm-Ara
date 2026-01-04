from widgets import PasswordField, ClickableLabel, PushButton, FieldStyleManager
from form_processor import FormProcessor
from notification_handler import NotificationHandler

from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Qt,
    Signal,
    QMargins
)
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QLineEdit,
    QVBoxLayout,
)


class LoginPanel(QFrame, FieldStyleManager):
    forgot_clicked = Signal()
    signup_clicked = Signal()
    continue_clicked = Signal()
    select_account_clicked = Signal()
    login_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    CONTENTS_MARGIN_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("LoginPanel")
        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(LoginPanel.CONTENTS_MARGIN_SIZE)
        layout.setSpacing(LoginPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap(":logos/logo.svg")
        logo.setPixmap(logo_file)
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
        self.email_input.setMaxLength(254)
        self.email_input.setObjectName("FieldLabel")
        layout.addWidget(self.email_input)

        # Password field
        password_label = QLabel("Password", self)
        password_label.setObjectName("FieldLabel")
        layout.addWidget(password_label)

        self.password_input = PasswordField(self)
        self.password_input.setObjectName("PasswordInput")
        self.password_input.input.setMaxLength(50)
        layout.addWidget(self.password_input)

        # Forgot password link
        forgot_label = ClickableLabel("Forgot your password?", self)
        forgot_label.clicked.connect(self.onForgotClicked)
        forgot_label.setAlignment(Qt.AlignRight)
        layout.addWidget(forgot_label)

        # Login button
        login_btn = PushButton("Login", self)
        login_btn.clicked.connect(self.onLoginClicked)
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

        # select account text
        select_account_label = ClickableLabel("Choose an Account", self)
        select_account_label.clicked.connect(self.onSelectAccountClicked)
        select_account_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(select_account_label)
        layout.addStretch(LoginPanel.STRETCH_SIZE)


    def onForgotClicked(self):
        self.forgot_clicked.emit()


    def onSignupClicked(self):
        self.signup_clicked.emit()


    def onCntClicked(self):
        self.continue_clicked.emit()


    def onSelectAccountClicked(self):
        self.select_account_clicked.emit()


    def onLoginClicked(self):
        field_map = {
            "email": self.email_input,
            "password": self.password_input.input
        }

        if not self.handleEmptyValidation(field_map):
            return

        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.login_clicked.emit(data)


    def handleFormatValidation(self, field_map):
        is_valid, result = self.form_processor.getValidationErrors(field_map)
        
        if not is_valid:
            form_fields = list(field_map.values())
            self.updateInvalidFieldStyle(result["invalid_widgets"], form_fields)
            
            errors = "\n".join(result["errors"])
            duration = max(4000, len(errors) * 50)
            
            self.notification_handler.showToast(
                "bottom_right", "Validation Errors",
                errors, "error", duration=duration
            )
            return False, None
            
        data = self.form_processor.getValidatedData(field_map)
        print(data)
        return True, data


    def handleEmptyValidation(self, field_map):
        form_fields = list(field_map.values())
        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        
        self.updateEmptyFieldStyle(field_status)
        
        if field_status["empty"]:
            self.notification_handler.showToast(
                "bottom_right", "Empty fields",
                "Please fill in all required fields.", "error", duration=5000
            )
            return False
        return True
