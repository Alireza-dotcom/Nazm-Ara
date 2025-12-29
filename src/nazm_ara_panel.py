from widgets import PushButton

from PySide6.QtCore import (
    Qt,
    QMargins,
)
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel
)


class TEMP(QFrame):
    STRETCH_SIZE = 1
    SPACING_SIZE = 13
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent, user_details):
        super().__init__(parent)
        self.setObjectName("BiNazm")
        self.user_details = user_details
        print(user_details)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(TEMP.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(TEMP.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)
        layout.addStretch(TEMP.STRETCH_SIZE)

        continue_btn = PushButton("Add Task", self)
        lbl = QLabel(str(self.user_details), self)
        lbl.setWordWrap(True)


        layout.addWidget(continue_btn)
        layout.addWidget(lbl)
        layout.addStretch(TEMP.STRETCH_SIZE)


        layout.addStretch(TEMP.STRETCH_SIZE)