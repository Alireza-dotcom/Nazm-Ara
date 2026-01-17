from widgets import ClickableLabel, PushButton, FieldStyleManager, FormRow
from notification_handler import NotificationHandler
from form_processor import FormProcessor

from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Qt,
    Signal,
    QMargins,
)
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout,
    QWidget
)


class ForgotPasswordPanel(QFrame, FieldStyleManager):
    """A UI panel that allows users to request a password reset email."""
    back_to_login_clicked = Signal()
    create_new_acc_clicked = Signal()
    reset_password_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("ForgotPasswordPanel")

        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(ForgotPasswordPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(ForgotPasswordPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        logo = QLabel(parent=self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        title = QLabel(text="Trouble logging in?", parent=self)
        title.setObjectName("TitleLabel")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.email = FormRow(label_text=f"Email{ForgotPasswordPanel.REQUIRED_FIELD}",
                             input_placeholder_text="example@hotmail.com",
                             input_max_length=254,
                             parent=self)
        layout.addWidget(self.email)

        self.reset_pass_btn = PushButton(text="Reset Password", parent=self)
        self.reset_pass_btn.clicked.connect(self.onResetPasswordClicked)
        layout.addWidget(self.reset_pass_btn)

        # Visual divider
        divider = QLabel(text="──────────  or  ──────────", parent=self)
        divider.setObjectName("DividerLabel")
        layout.addWidget(divider, alignment=Qt.AlignmentFlag.AlignCenter)

        create_new_acc_label = ClickableLabel(text="Create new account", parent=self)
        create_new_acc_label.clicked.connect(lambda: self.create_new_acc_clicked.emit())
        layout.addWidget(create_new_acc_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        back_to_login_btn = PushButton(text="Back to login", parent=self)
        back_to_login_btn.clicked.connect(lambda: self.back_to_login_clicked.emit())
        layout.addWidget(back_to_login_btn)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)


    def onResetPasswordClicked(self):
        """Executes the validation process before emitting the reset signal."""
        field_map = {
            "email": self.email.input,
        }

        # Step 1: Ensure fields aren't blank
        if not self.handleEmptyValidation(field_map):
            return

        # Step 2: Ensure data is formatted correctly
        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.reset_password_clicked.emit(data)


    def handleFormatValidation(self, field_map: dict):
        """Checks if the provided email follows correct syntax."""
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
            
        # If valid, extract the cleaned data
        data = self.form_processor.getValidatedData(field_map)
        return True, data


    def handleEmptyValidation(self, field_map: dict):
        """Checks if any required fields are left empty."""
        form_fields = list(field_map.values())
        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        
        # Update field UI styles based on whether they are empty or filled
        self.updateEmptyFieldStyle(field_status)
        
        if field_status.get("empty"):
            self.notification_handler.showToast(
                "bottom_right", "Empty fields",
                "Please fill in email field.", "error", duration=3000
            )
            return False
        return True
