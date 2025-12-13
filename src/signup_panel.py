from widgets import PasswordField, ClickableLabel, PushButton, FormRow

from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Qt,
    Signal,
    QMargins,
    QSize,
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

    STRETCH_SIZE = 1
    SPACING_SIZE = 10
    LOGO_SIZE = QSize(200, 200)
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SignupPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SignupPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SignupPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap("../res/logos/logo.png")
        logo_file = logo_file.scaled(SignupPanel.LOGO_SIZE)
        logo.setPixmap(QPixmap(logo_file))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # Title
        title = QLabel("Create a new account", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # first name field and label
        first_name = FormRow(label_text="First Name",\
                             object_name="FieldLabel",\
                             parent=self)

        # last name field and label
        last_name = FormRow(label_text="First Name",\
                            object_name="FieldLabel",\
                            parent=self)

        #name layout
        name_layout = QHBoxLayout()
        name_layout.addWidget(first_name)
        name_layout.addWidget(last_name)
        layout.addLayout(name_layout)

        # display name field
        display_name_label = QLabel("Display name", self)
        display_name_label.setObjectName("FieldLabel")
        layout.addWidget(display_name_label)

        self.display_name_input = QLineEdit(self)
        layout.addWidget(self.display_name_input)

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

        # signup button
        signup_btn = PushButton("Sign up", self)
        layout.addWidget(signup_btn)
        layout.addStretch(SignupPanel.STRETCH_SIZE)

        # already have account link
        already_have_acc_label = ClickableLabel("Already have an account?", self)
        already_have_acc_label.clicked.connect(self.onBackToLoginClicked)
        already_have_acc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(already_have_acc_label)

    def onBackToLoginClicked(self):
        self.already_have_account_clicked.emit()
