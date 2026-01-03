from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QCalendarWidget
)
from PySide6.QtGui import (
    QIcon,
    QColor,
    QTextCharFormat,
    QBrush,
)
from PySide6.QtCore import (
    QSize,
    QMargins,
    Signal,
    Qt
)


class RadioButton(QPushButton):
    # Tracks the currently active button across all instances
    active_button = None

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.clicked.connect(self.handle_click)
        self.update_style()

    def mousePressEvent(self, event):
        # If already pushed, do nothing
        if self.isChecked():
            return 
        super().mousePressEvent(event)

    def handle_click(self):
        # Uncheck the previous button if it exists
        if RadioButton.active_button and RadioButton.active_button != self:
            RadioButton.active_button.setChecked(False)
            RadioButton.active_button.update_style()

        self.setChecked(True)
        RadioButton.active_button = self
        self.update_style()

    def update_style(self):
        if self.isChecked():
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)


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

        self.input = QLineEdit(self)
        self.input.setEchoMode(QLineEdit.Password)

        # Create the toggle button
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(self.eye_open_icon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(PasswordField.PASS_VISIBILITY_BTN_SIZE)
        self.toggle_button.clicked.connect(self.togglePasswordVisibility)

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.input)
        layout.addWidget(self.toggle_button)
        layout.setContentsMargins(PasswordField.CONTENTS_MARGINS_SIZE)
        self.setLayout(layout)


    def togglePasswordVisibility(self):
        if self.toggle_button.isChecked():
            self.input.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setIcon(self.eye_close_icon)
        else:
            self.input.setEchoMode(QLineEdit.Password)
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


class TodoListItemWidget(QWidget):
    on_check_button_clicked = Signal(object, str, int)


    CONTENTS_MARGINS_SIZE = QMargins(20, 20, 20, 20)
    SPACING_SIZE = 15
    STRETCH_SIZE = 1

    def __init__(self, todo_details: dict, parent=None):
        super().__init__(parent)

        self.todo_details = todo_details
        layout = QHBoxLayout(self)
        layout.setContentsMargins(TodoListItemWidget.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(TodoListItemWidget.SPACING_SIZE)
        desc_and_title_layout = QVBoxLayout()
        text_and_check_box_layout = QHBoxLayout()

        title_text = self.todo_details["title"]
        description_text = self.todo_details["description"]
        self.check_btn = PushButton(self)
        self.check_btn.setObjectName("TaskButton")
        self.check_btn.setCheckable(True)
        self.check_btn.clicked.connect(self.checkBtnClicked)
        self.check_btn.setFixedSize(25, 25)


        self.title_label = QLabel(title_text, self)
        self.title_label.setObjectName("TaskTitle")

        todo_prio = self.todo_details["priority"]
        self.priority_label_text = self.getPriorityText(todo_prio)
        self.priority_label_obj_name = self.getPriorityText(todo_prio) #"Low", "Medium", "High"
        self.priority_type_lbl = QLabel(self.priority_label_text, self)
        self.priority_type_lbl.setObjectName(self.priority_label_obj_name)
        self.priority_type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignVCenter)
        self.priority_type_lbl.setFixedSize(70, 30)
        self.priority_type_lbl.setMargin(5)

        self.desc_label = QLabel(description_text, self)
        self.desc_label.setObjectName("TaskDesc")

        self.edit_btn = PushButton(self)
        self.edit_btn.setObjectName("EditButton")
        self.edit_btn.setIcon(QIcon(":/icons/edit.svg"))
        self.edit_btn.setFixedSize(30, 30)

        text_and_check_box_layout.addWidget(self.check_btn)
        text_and_check_box_layout.addWidget(self.title_label)
        text_and_check_box_layout.addWidget(self.priority_type_lbl)

        desc_and_title_layout.addLayout(text_and_check_box_layout)
        desc_and_title_layout.addWidget(self.desc_label)

        layout.addLayout(desc_and_title_layout)
        layout.addStretch(TodoListItemWidget.STRETCH_SIZE)
        layout.addWidget(self.edit_btn)

        if self.todo_details.get("is_complete"):
            self.check_btn.setChecked(True)
            self.toggleCheckedBtn()


    def checkBtnClicked(self):
        task_id = self.todo_details["local_id"]
        btn_value = self.check_btn.isChecked()
        self.on_check_button_clicked.emit(self, task_id, btn_value)

    def toggleCheckedBtn(self):
        if self.check_btn.isChecked():
            btn_font = self.title_label.font()
            btn_font.setStrikeOut(True)
            self.title_label.setFont(btn_font)
        else:
            btn_font = self.title_label.font()
            btn_font.setStrikeOut(False)
            self.title_label.setFont(btn_font)



    def getPriorityText(self, priority):
        mapping = {
            0: "Low",
            1: "Medium",
            2: "High"
        }
        
        return mapping.get(priority, "unknown")


class TodoCalendar(QCalendarWidget):
    day_changed = Signal(object)

    def __init__(self, current_day, parent=None):
        super().__init__(parent)
        self.current_day = current_day
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setGridVisible(True)
        self.setFixedSize(280, 280)

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.ClickFocus)
        
        self.todo_format = QTextCharFormat()
        self.todo_format.setBackground(QBrush(QColor("#2D2926")))

        self.selectionChanged.connect(self.onSelectionChanged)


    def setTodoDates(self, dates_list):
        for date in dates_list:
            self.setDateTextFormat(date, self.todo_format)


    def onSelectionChanged(self):
        self.day_changed.emit(self.selectedDate())
        self.hide()
