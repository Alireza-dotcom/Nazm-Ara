from widgets import ClickableLabel, PushButton, FieldStyleManager, FormRow
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
    QVBoxLayout,
    QWidget
)


class LoginPanel(QFrame, FieldStyleManager):
    """A UI panel that handles user authentication."""
    signup_clicked = Signal()
    continue_clicked = Signal()
    login_clicked = Signal(dict)
    select_account_clicked = Signal()
    forgot_password_clicked = Signal()

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    CONTENTS_MARGIN_SIZE = QMargins(50, 40, 50, 40)
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("LoginPanel")
        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(LoginPanel.CONTENTS_MARGIN_SIZE)
        layout.setSpacing(LoginPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        logo = QLabel(parent=self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        title = QLabel(text="Login", parent=self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.email = FormRow(label_text=f"Email{LoginPanel.REQUIRED_FIELD}",
                             input_placeholder_text="example@hotmail.com",
                             input_max_length=254,
                             parent=self)
        layout.addWidget(self.email)

        self.password = FormRow(label_text=f"Password{LoginPanel.REQUIRED_FIELD}",
                             input_placeholder_text="********",
                             input_max_length=50,
                             is_pass_field=True,
                             parent=self)
        layout.addWidget(self.password)

        forgot_label = ClickableLabel(text="Forgot your password?", parent=self)
        forgot_label.clicked.connect(lambda: self.forgot_password_clicked.emit())
        layout.addWidget(forgot_label, alignment=Qt.AlignmentFlag.AlignRight)

        login_btn = PushButton(text="Login", parent=self)
        login_btn.clicked.connect(self.onLoginClicked)
        layout.addWidget(login_btn)

        # Visual divider
        divider = QLabel(text="──────────  or continue offline  ──────────", parent=self)
        divider.setObjectName("DividerLabel")
        layout.addWidget(divider, alignment=Qt.AlignmentFlag.AlignCenter)

        self.continue_btn = PushButton(text="Continue without Account", parent=self)
        self.continue_btn.clicked.connect(lambda: self.continue_clicked.emit())
        layout.addWidget(self.continue_btn)

        signup_label = ClickableLabel(text="Don't have an account? Sign up", parent=self)
        signup_label.clicked.connect(lambda: self.signup_clicked.emit())
        layout.addWidget(signup_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(LoginPanel.STRETCH_SIZE)

        select_account_label = ClickableLabel(text="Choose an Account", parent=self)
        select_account_label.clicked.connect(lambda: self.select_account_clicked.emit())
        layout.addWidget(select_account_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(LoginPanel.STRETCH_SIZE)


    def onLoginClicked(self):
        """Checks the validation process before emitting the login signal."""
        field_map = {
            "email": self.email.input,
            "password": self.password.password_field.input
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
