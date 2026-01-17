from widgets import (
    ClickableLabel,
    PushButton, FormRow,
    FieldStyleManager
)
from form_processor import FormProcessor
from notification_handler import NotificationHandler

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
    QHBoxLayout,
    QWidget
)


class SignupPanel(QFrame, FieldStyleManager):
    """UI panel for user registration."""
    already_have_account_clicked = Signal()
    signup_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("SignupPanel")

        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SignupPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SignupPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        logo = QLabel(parent=self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        title = QLabel(text="Create a new account", parent=self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.first_name = FormRow(label_text=f"First Name{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza",
                             input_max_length=30,
                             parent=self)
        layout.addWidget(self.first_name)

        self.last_name = FormRow(label_text=f"Last Name{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Amiri",
                             input_max_length=30,
                             parent=self)
        layout.addWidget(self.last_name)

        # Horizontal layout to place First and Last name side-by-side
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.first_name)
        name_layout.addWidget(self.last_name)
        layout.addLayout(name_layout)

        self.display_name = FormRow(label_text=f"Display name{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza_koochak_khan",
                             input_max_length=25,
                             parent=self)
        layout.addWidget(self.display_name)

        self.email = FormRow(label_text=f"Email{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="example@hotmail.com",
                             input_max_length=254,
                             parent=self)
        layout.addWidget(self.email)

        self.password = FormRow(label_text=f"Password{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="********",
                             input_max_length=50,
                             is_pass_field=True,
                             parent=self)
        layout.addWidget(self.password)

        self.signup_btn = PushButton(text="Sign up", parent=self)
        self.signup_btn.clicked.connect(self.onSignupClicked)
        layout.addWidget(self.signup_btn)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        already_have_acc_label = ClickableLabel(text="Already have an account?", parent=self)
        already_have_acc_label.clicked.connect(lambda: self.already_have_account_clicked.emit())
        already_have_acc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(already_have_acc_label)


    def onSignupClicked(self):
        """Checks the validation process before emitting the create online user signal."""
        field_map = {
            "first_name": self.first_name.input,
            "last_name": self.last_name.input,
            "nickname": self.display_name.input,
            "email": self.email.input,
            "password": self.password.password_field.input,
        }

        # Step 1: Ensure fields aren't blank
        if not self.handleEmptyValidation(field_map):
            return

        # Step 2: Ensure data format is correct
        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.signup_clicked.emit(data)


    def handleFormatValidation(self, field_map: dict):
        """Checks formatting and displays notifications for invalid input."""
        is_valid, result = self.form_processor.getValidationErrors(field_map, is_signup=True)

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
