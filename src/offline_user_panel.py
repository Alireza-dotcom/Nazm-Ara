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
    """Panel for creating a local offline profile."""
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

        logo = QLabel(self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

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

        # Horizontal layout to place First and Last name side-by-side
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.first_name)
        name_layout.addWidget(self.last_name)
        layout.addLayout(name_layout)

        display_name_label = QLabel("Display name", self)
        display_name_label.setObjectName("FieldLabel")
        layout.addWidget(display_name_label)

        self.display_name_input = QLineEdit(self)
        self.display_name_input.setMaxLength(25)
        layout.addWidget(self.display_name_input)

        continue_btn = PushButton("Continue", self)
        continue_btn.clicked.connect(self.onContinueClicked)
        layout.addWidget(continue_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        back_to_login_btn = PushButton("Back to login", self)
        back_to_login_btn.clicked.connect(lambda: self.back_to_login_clicked.emit())
        layout.addWidget(back_to_login_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)


    def onContinueClicked(self):
        """Checks the validation process before emitting the create offline user signal."""
        field_map = {
            "first_name": self.first_name.input,
            "last_name": self.last_name.input,
            "nickname": self.display_name_input,
        }

        # Step 1: Ensure fields aren't blank
        if not self.handleEmptyValidation(field_map):
            return

        # Step 2: Ensure data format is correct
        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        self.continue_clicked.emit(data)


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
