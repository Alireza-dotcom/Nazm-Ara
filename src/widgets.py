from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
)

from PySide6.QtCore import Qt, Signal, QSize, QMargins
from PySide6.QtGui import QPixmap


class PushButton(QPushButton):
    def __init__(self, text="" , parent=None):
        super().__init__(text, parent)

        self.setCursor(Qt.PointingHandCursor)


class PasswordField(QWidget):
    PASS_VISIBILITY_BTN_SIZE = QSize(35, 35)
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.eye_close_icon = QPixmap(":icons/eye_close.svg")
        self.eye_open_icon  = QPixmap(":icons/eye_open.svg")

        self.line_edit = QLineEdit(self)
        self.line_edit.setEchoMode(QLineEdit.Password)

        # Create the toggle button
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(self.eye_open_icon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(PasswordField.PASS_VISIBILITY_BTN_SIZE)
        self.toggle_button.clicked.connect(self.togglePasswordVisibility)

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.toggle_button)
        layout.setContentsMargins(PasswordField.CONTENTS_MARGINS_SIZE)
        self.setLayout(layout)


    def togglePasswordVisibility(self):
        if self.toggle_button.isChecked():
            self.line_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setIcon(self.eye_close_icon)
        else:
            self.line_edit.setEchoMode(QLineEdit.Password)
            self.toggle_button.setIcon(self.eye_open_icon)


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pressed = True
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if self._mouse_pressed and event.button() == Qt.LeftButton:
            if self.rect().contains(event.position().toPoint()): # Released inside label
                self.clicked.emit()
        self._mouse_pressed = False
        super().mouseReleaseEvent(event)


class FormRow(QWidget):
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, label_text, object_name, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(FormRow.CONTENTS_MARGINS_SIZE)

        self.label = QLabel(label_text, self)
        self.input = QLineEdit(self)
        self.setObjectName(object_name)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
