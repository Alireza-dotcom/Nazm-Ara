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
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("OfflineUserPanel")
        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(OfflineUserPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(OfflineUserPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        logo = QLabel(parent=self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        title = QLabel(text="Set Up Your Profile", parent=self)
        title.setObjectName("TitleLabel")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.first_name = FormRow(label_text=f"First Name{OfflineUserPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza",
                             input_max_length=30,
                             parent=self)
        layout.addWidget(self.first_name)

        self.last_name = FormRow(label_text=f"Last Name{OfflineUserPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Amiri",
                             input_max_length=30,
                             parent=self)
        layout.addWidget(self.last_name)

        # Horizontal layout to place First and Last name side-by-side
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.first_name)
        name_layout.addWidget(self.last_name)
        layout.addLayout(name_layout)

        self.display_name = FormRow(label_text=f"Display name{OfflineUserPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza_koochak_khan",
                             input_max_length=25,
                             parent=self)
        layout.addWidget(self.display_name)

        continue_btn = PushButton(text="Continue", parent=self)
        continue_btn.clicked.connect(self.onContinueClicked)
        layout.addWidget(continue_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        back_to_login_btn = PushButton(text="Back to login", parent=self)
        back_to_login_btn.clicked.connect(lambda: self.back_to_login_clicked.emit())
        layout.addWidget(back_to_login_btn)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)


    def onContinueClicked(self):
        """Checks the validation process before emitting the create offline user signal."""
        field_map = {
            "first_name": self.first_name.input,
            "last_name": self.last_name.input,
            "nickname": self.display_name.input,
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
