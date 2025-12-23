from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
)

from PySide6.QtCore import Qt, Signal, QSize, QMargins
from PySide6.QtGui import QIcon


class PushButton(QPushButton):
    def __init__(self, text="" , parent=None):
        super().__init__(text, parent)

        self.setCursor(Qt.PointingHandCursor)


class PasswordField(QWidget):
    PASS_VISIBILITY_BTN_SIZE = QSize(40, 40)
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.eye_close_icon = QIcon(":icons/eye_close.svg")
        self.eye_open_icon  = QIcon(":icons/eye_open.svg")

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


class AccountListItemWidget(QWidget):
    def __init__(self, account_row: dict, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        text_layout = QVBoxLayout()

        title_text = self.formatTitle(account_row)
        subtitle_text = self.formatSubtitle(account_row)

        self.title_label = QLabel(title_text, self)
        self.title_label.setObjectName("ItemTitle")

        self.sub_label = QLabel(subtitle_text, self)
        self.sub_label.setObjectName("ItemSub")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.sub_label)

        layout.addLayout(text_layout)

        acc_type_label_txt = "Online" if self.isOnlineAccount(account_row) else "Offline"
        acc_type_label_obj_name = "onlineLabel" if self.isOnlineAccount(account_row) else "offlineLabel"

        self.acc_type_lbl = QLabel(acc_type_label_txt, self)
        self.acc_type_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.acc_type_lbl.setObjectName(acc_type_label_obj_name)
        self.acc_type_lbl.setFixedSize(50, 30)
        self.acc_type_lbl.setMargin(5)
        layout.addWidget(self.acc_type_lbl)


    def formatTitle(self, account_row: dict) -> str:
        nickname = account_row.get("nickname")
        if nickname:
            return nickname
        return f"Account #{account_row.get('id', '?')}"


    def formatSubtitle(self, account_row: dict) -> str:
        email = account_row.get("email")
        f_name = account_row.get("f_name")
        l_name = account_row.get("l_name")
        if email:
            return email
        name_parts = [p for p in [f_name, l_name] if p]
        if name_parts:
            return " ".join(name_parts)
        return f"ID: {account_row.get('id', '?')}"


    def isOnlineAccount(self, account_row: dict) -> bool:
        return account_row.get("user_id") is not None