from widgets import PushButton
from form_processor import FormProcessor
from widgets import FormRow, ScalableSvgWidget
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


class OfflineUserPanel(QFrame):
    """Panel for creating a local offline profile."""
    back_to_login_clicked = Signal()
    continue_clicked = Signal(dict)

    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("OfflineUserPanel")
        self.form_processor = FormProcessor(parent=self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(OfflineUserPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(OfflineUserPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        logo = ScalableSvgWidget(svg_path=":logos/logo.svg", parent=self)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(OfflineUserPanel.STRETCH_SIZE)

        title = QLabel(text="Set Up Your Profile", parent=self)
        title.setObjectName("TitleLabel")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.first_name = FormRow(label_text=f"First Name{OfflineUserPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza",
                             input_max_length=30,
                             input_validator_regex="^[a-zA-Z\u0600-\u06FF\s']+$",
                             parent=self)
        layout.addWidget(self.first_name)

        self.last_name = FormRow(label_text=f"Last Name{OfflineUserPanel.REQUIRED_FIELD}",
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

        self.display_name = FormRow(label_text=f"Display name{OfflineUserPanel.REQUIRED_FIELD}",
                             input_placeholder_text="Mirza_koochak_khan",
                             input_max_length=25,
                             input_validator_regex="^[a-zA-Z\u0600-\u06FF0-9_']+$",
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
        field_map = [
            {"field_name": "first_name", "field_input": self.first_name.input,  "field_object": self.first_name,   "min_length": 3},
            {"field_name": "last_name",  "field_input": self.last_name.input,   "field_object": self.last_name,    "min_length": 3},
            {"field_name": "nickname",   "field_input": self.display_name.input,"field_object": self.display_name, "min_length": 3},
        ]

        data = self.form_processor.authenticationValidator(field_map)
        if not data:
            return

        self.continue_clicked.emit(data)
