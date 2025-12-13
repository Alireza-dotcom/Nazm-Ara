from widgets import ClickableLabel, PushButton

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


class ForgotPasswordPanel(QFrame):
    back_to_login_clicked = Signal()
    create_new_acc_clicked = Signal()

    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    LOGO_SIZE = QSize(250, 250)
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ForgotPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(ForgotPasswordPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(ForgotPasswordPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap("../res/logos/logo.png")
        logo_file = logo_file.scaled(ForgotPasswordPanel.LOGO_SIZE)
        logo.setPixmap(QPixmap(logo_file))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        # Title
        title = QLabel("Trouble logging in?", self)
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

        # reset password button
        reset_pass_btn = PushButton("Reset Password", self)
        layout.addWidget(reset_pass_btn)

        # Divider
        divider = QLabel("──────────  or  ──────────", self)
        divider.setAlignment(Qt.AlignCenter)
        divider.setObjectName("DividerLabel")
        layout.addWidget(divider)

        # Create new account button
        create_new_acc_label = ClickableLabel("Create new account", self)
        create_new_acc_label.clicked.connect(self.onCreateNewAccClicked)
        create_new_acc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(create_new_acc_label)

        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        # back to login page button
        back_to_login_btn = PushButton("Back to login", self)
        back_to_login_btn.clicked.connect(self.onBackToLoginClicked)
        layout.addWidget(back_to_login_btn)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

    def onBackToLoginClicked(self):
        self.back_to_login_clicked.emit()

    def onCreateNewAccClicked(self):
        self.create_new_acc_clicked.emit()

