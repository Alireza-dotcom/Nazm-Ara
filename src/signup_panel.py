from widgets import (
    ClickableLabel,
    PushButton,
    FormRow,
    ScalableSvgWidget
)
from form_processor import FormProcessor
from PySide6.QtCore import (
    Qt,
    Signal,
    QMargins
)
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
)


class SignupPanel(QFrame):
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

        self.form_processor = FormProcessor(parent=self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SignupPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SignupPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        logo = ScalableSvgWidget(svg_path=":logos/logo.svg", parent=self)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        title = QLabel(text="Create a new account", parent=self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.first_name = FormRow(label_text=f"First Name{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza",
                             input_max_length=30,
                             input_validator_regex="^[a-zA-Z\u0600-\u06FF\s']+$",
                             parent=self)
        layout.addWidget(self.first_name)

        self.last_name = FormRow(label_text=f"Last Name{SignupPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Amiri",
                             input_max_length=30,
                             input_validator_regex="^[a-zA-Z\u0600-\u06FF\s']+$",
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
                             input_validator_regex="^[a-zA-Z\u0600-\u06FF0-9_']+$",
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
        field_map = [
            {"field_name": "password",   "field_input": self.password.pass_field.input, "field_object": self.password,     "min_length": 8, "quality_check": True},
            {"field_name": "first_name", "field_input": self.first_name.input,          "field_object": self.first_name,   "min_length": 3},
            {"field_name": "last_name",  "field_input": self.last_name.input,           "field_object": self.last_name,    "min_length": 3},
            {"field_name": "nickname",   "field_input": self.display_name.input,        "field_object": self.display_name, "min_length": 3},
            {"field_name": "email",      "field_input": self.email.input,               "field_object": self.email}
        ]

        data = self.form_processor.authenticationValidator(field_map)
        if not data:
            return

        self.signup_clicked.emit(data)
