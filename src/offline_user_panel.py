from widgets import PushButton, FieldStyleManager
from notification_handler import NotificationHandler
from form_processor import FormProcessor
from widgets import FormRow

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


class OfflineUserPanel(QFrame, FieldStyleManager):
    back_to_login_clicked = Signal()
    continue_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("OfflineUserPanel")
        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(OfflineUserPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(OfflineUserPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        # Logo placeholder
        logo = QLabel(self)
        logo_file = QPixmap(":logos/logo.svg")
        logo.setPixmap(logo_file)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        # Title
        title = QLabel("Set Up Your Profile", self)
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

        # continue button
        continue_btn = PushButton("Continue", self)
        continue_btn.clicked.connect(self.onContinueClicked)
        layout.addWidget(continue_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)


        # back to login page button
        back_to_login_btn = PushButton("Back to login", self)
        back_to_login_btn.clicked.connect(self.onBackToLoginClicked)
        layout.addWidget(back_to_login_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)


    def onBackToLoginClicked(self):
        self.back_to_login_clicked.emit()


    def onContinueClicked(self):
        field_map = {
            "first_name": self.first_name.input,
            "last_name": self.last_name.input,
            "nickname": self.display_name_input,
        }

        if not self.handleEmptyValidation(field_map):
            return

        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.continue_clicked.emit(data)


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
                "Please fill in all required fields.", "error", duration=5000
            )
            return False
        return True
