from widgets import ClickableLabel, PushButton
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
    QLineEdit,
    QVBoxLayout,
)


class ForgotPasswordPanel(QFrame):
    back_to_login_clicked = Signal()
    create_new_acc_clicked = Signal()
    reset_password_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ForgotPasswordPanel")
        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(ForgotPasswordPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(ForgotPasswordPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(ForgotPasswordPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap(":logos/logo.svg")
        logo.setPixmap(logo_file)
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
        self.email_input.setMaxLength(254)
        layout.addWidget(self.email_input)

        # reset password button
        reset_pass_btn = PushButton("Reset Password", self)
        reset_pass_btn.clicked.connect(self.onResetPasswordClicked)
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


    def onResetPasswordClicked(self):
        field_map = {
            "email": self.email_input,
        }

        if not self.handleEmptyValidation(field_map):
            return

        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.reset_password_clicked.emit(data)


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

        return True, data


    def handleEmptyValidation(self, field_map):
        form_fields = list(field_map.values())
        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        
        self.updateEmptyFieldStyle(field_status)
        
        if field_status["empty"]:
            self.notification_handler.showToast(
                "bottom_right", "Empty fields",
                "Please fill in email field.", "error", duration=5000
            )
            return False
        return True


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
