from widgets import PasswordField, ClickableLabel, PushButton, FormRow
from form_preprocessor import FormProcessor
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
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
)


class SignupPanel(QFrame):
    already_have_account_clicked = Signal()
    signup_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SignupPanel")

        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SignupPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SignupPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap(":logos/logo.svg")
        logo.setPixmap(logo_file)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # Title
        title = QLabel("Create a new account", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # first name field and label
        self.first_name = FormRow(label_text="First Name",\
                             object_name="FieldLabel",\
                             parent=self)
        self.first_name.input.setMaxLength(30)

        # last name field and label
        self.last_name = FormRow(label_text="Last Name",\
                            object_name="FieldLabel",\
                            parent=self)
        self.last_name.input.setMaxLength(30)

        #name layout
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.first_name)
        name_layout.addWidget(self.last_name)
        layout.addLayout(name_layout)

        # display name field
        display_name_label = QLabel("Display name", self)
        display_name_label.setObjectName("FieldLabel")
        layout.addWidget(display_name_label)

        self.display_name_input = QLineEdit(self)
        self.display_name_input.setMaxLength(25)
        layout.addWidget(self.display_name_input)

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
        self.password_input.input.setMaxLength(50)
        self.password_input.setObjectName("PasswordInput")
        layout.addWidget(self.password_input)

        # signup button
        self.signup_btn = PushButton("Sign up", self)
        self.signup_btn.clicked.connect(self.onSignupClicked)
        layout.addWidget(self.signup_btn)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # already have account link
        already_have_acc_label = ClickableLabel("Already have an account?", self)
        already_have_acc_label.clicked.connect(self.onBackToLoginClicked)
        already_have_acc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(already_have_acc_label)


    def onBackToLoginClicked(self):
        self.already_have_account_clicked.emit()


    def onSignupClicked(self):
        field_map = {
            "first_name": self.first_name.input,
            "last_name": self.last_name.input,
            "nickname": self.display_name_input,
            "email": self.email_input,
            "password": self.password_input.input,
        }
        form_fields = list(field_map.values())

        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        self.updateEmptyFieldStyle(field_status)
        if field_status["empty"]:
            self.notification_handler.showToast(
            "bottom_right",
            "Empty fields",
            "Please fill in all required fields.",
            "error",
            duration=5000,
            )

            return

        is_valid, result = self.form_processor.validateSignupFields(field_map)
        if not is_valid:
            self.updateInvalidFieldStyle(result["invalid_widgets"], form_fields)
            errors = "\n".join(result["errors"])

            calculate_duration = max(4000, len(errors) * 50)  # 50 ms per character
            self.notification_handler.showToast(
            "bottom_right",
            "Validation erros",
            errors, "error",
            duration=calculate_duration,
            )

            return

        self.signup_clicked.emit(result)

    def updateEmptyFieldStyle(self, fields):
        for field in fields["empty"]:
            field.setStyleSheet("QLineEdit { border: 1px solid red; }")

        for field in fields["filled"]:
            field.setStyleSheet("")


    def updateInvalidFieldStyle(self, invalid_fields, all_fields):
        for field in all_fields:
            if field in invalid_fields:
                field.setStyleSheet("QLineEdit { border: 1px solid red; }")
            else:
                field.setStyleSheet("")
