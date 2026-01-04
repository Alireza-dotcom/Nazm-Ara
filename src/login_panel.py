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
    """A UI panel that handles user authentication."""
    forgot_password_clicked = Signal()
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

        logo = QLabel(self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        title = QLabel("Login", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        email_label = QLabel("Email", self)
        email_label.setObjectName("FieldLabel")
        layout.addWidget(email_label)

        self.email_input = QLineEdit(self)
        self.email_input.setMaxLength(254)
        self.email_input.setObjectName("FieldLabel")
        layout.addWidget(self.email_input)

        password_label = QLabel("Password", self)
        password_label.setObjectName("FieldLabel")
        layout.addWidget(password_label)

        self.password_input = PasswordField(self)
        self.password_input.setObjectName("PasswordInput")
        self.password_input.input.setMaxLength(50)
        layout.addWidget(self.password_input)

        forgot_label = ClickableLabel("Forgot your password?", self)
        forgot_label.clicked.connect(lambda: self.forgot_password_clicked.emit())
        forgot_label.setAlignment(Qt.AlignRight)
        layout.addWidget(forgot_label)

        login_btn = PushButton("Login", self)
        login_btn.clicked.connect(self.onLoginClicked)
        layout.addWidget(login_btn)

        # Visual divider
        divider = QLabel("──────────  or continue offline  ──────────", self)
        divider.setAlignment(Qt.AlignCenter)
        divider.setObjectName("DividerLabel")
        layout.addWidget(divider)

        self.cont_btn = PushButton("Continue without Account", self)
        layout.addWidget(self.cont_btn)
        self.cont_btn.clicked.connect(lambda: self.continue_clicked.emit())

        signup_label = ClickableLabel("Don't have an account? Sign up", self)
        signup_label.clicked.connect(lambda: self.signup_clicked.emit())
        signup_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(signup_label)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        select_account_label = ClickableLabel("Choose an Account", self)
        select_account_label.clicked.connect(lambda: self.select_account_clicked.emit())
        select_account_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(select_account_label)
        layout.addStretch(LoginPanel.STRETCH_SIZE)


    def onLoginClicked(self):
        """Checks the validation process before emitting the login signal."""
        field_map = {
            "email": self.email_input,
            "password": self.password_input.input
        }

        # Step 1: Ensure fields aren't blank
        if not self.handleEmptyValidation(field_map):
            return

        # Step 2: Ensure data format is correct
        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.login_clicked.emit(data)


    def handleFormatValidation(self, field_map: dict):
        """Checks formatting and displays notifications for invalid input."""
        is_valid, result = self.form_processor.getValidationErrors(field_map)
        
        if not is_valid:
            form_fields = list(field_map.values())
            self.updateInvalidFieldStyle(result.get("invalid_widgets"), form_fields)
            
            # Show a toast notification with the specific error reasons
            errors = "\n".join(result.get("errors"))
            duration = max(4000, len(errors) * 50)
            
            self.notification_handler.showToast(
                "bottom_right", "Validation Errors",
                errors, "error", duration=duration
            )
            return False, None
            
        data = self.form_processor.getValidatedData(field_map)
        return True, data


    def handleEmptyValidation(self, field_map: dict):
        """Checks for missing input and provides visual feedback."""
        form_fields = list(field_map.values())
        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        
        # Update field UI styles based on whether they are empty or filled
        self.updateEmptyFieldStyle(field_status)
        
        if field_status.get("empty"):
            self.notification_handler.showToast(
                "bottom_right", "Empty fields",
                "Please fill in all required fields.", "error", duration=5000
            )
            return False
        return True
