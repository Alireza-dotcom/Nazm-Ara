from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QCalendarWidget,
    QApplication
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
    Qt,
    QDate
)


class RadioButton(QPushButton):
    """
    Custom button that behaves like a RadioButton.
    Only one instance can be active at a time across the application.
    """
    # Tracks the currently active button across all instances
    active_button = None

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.clicked.connect(self.handle_click)
        self.update_style()

    def mousePressEvent(self, event):
        # Prevents unchecking a button by clicking it again once active
        if self.isChecked():
            return 
        super().mousePressEvent(event)

    def handle_click(self):
        """Ensures only one option is active."""
        if RadioButton.active_button and RadioButton.active_button != self:
            RadioButton.active_button.setChecked(False)
            RadioButton.active_button.update_style()

        self.setChecked(True)
        RadioButton.active_button = self
        self.update_style()

    def update_style(self):
        """Changes the cursor to indicate whether the button is interactable."""
        if self.isChecked():
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)


class PushButton(QPushButton):
    """QPushButton with a pointing hand cursor for better UX."""
    def __init__(self, text="" , parent=None):
        super().__init__(text, parent)

        self.setCursor(Qt.PointingHandCursor)


class PasswordField(QWidget):
    """
    Composite widget containing a QLineEdit and a toggle button 
    to switch between masked (password) and plain text visibility.
    """
    PASS_VISIBILITY_BTN_SIZE = QSize(40, 40)
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.eye_close_icon = QIcon(":icons/eye_close.svg")
        self.eye_open_icon  = QIcon(":icons/eye_open.svg")

        self.input = QLineEdit(self)
        self.input.setEchoMode(QLineEdit.Password)

        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(self.eye_open_icon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(PasswordField.PASS_VISIBILITY_BTN_SIZE)
        self.toggle_button.clicked.connect(self.togglePasswordVisibility)

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
    """A QLabel that behaves like a button, emitting a clicked signal."""
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pressed = True
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        """Emits clicked signal only if the mouse is released inside the label area."""
        if self._mouse_pressed and event.button() == Qt.LeftButton:
            if self.rect().contains(event.position().toPoint()): # Released inside label
                self.clicked.emit()
        self._mouse_pressed = False
        super().mouseReleaseEvent(event)


class FormRow(QWidget):
    """Helper widget that groups a Label and a LineEdit vertically for forms."""
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, label_text: str, object_name: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(FormRow.CONTENTS_MARGINS_SIZE)

        self.label = QLabel(label_text, self)
        self.input = QLineEdit(self)
        # Applying object name to the widget for QSS targeting
        self.setObjectName(object_name)

        layout.addWidget(self.label)
        layout.addWidget(self.input)


class AccountListItemWidget(QWidget):
    """Custom widget for account selection list items, showing user info and account type."""
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

        # Logic to display "Online" vs "Offline" badge
        acc_type_label_txt = "Online" if self.isOnlineAccount(account_row) else "Offline"
        acc_type_label_obj_name = "onlineLabel" if self.isOnlineAccount(account_row) else "offlineLabel"

        self.acc_type_lbl = QLabel(acc_type_label_txt, self)
        self.acc_type_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.acc_type_lbl.setObjectName(acc_type_label_obj_name)
        self.acc_type_lbl.setFixedSize(50, 30)
        self.acc_type_lbl.setMargin(5)
        layout.addWidget(self.acc_type_lbl)


    def formatTitle(self, account_row: dict) -> str:
        """Returns nickname or a fallback ID-based string."""
        nickname = account_row.get("nickname")
        if nickname:
            return nickname
        return f"Account #{account_row.get('id', '?')}"


    def formatSubtitle(self, account_row: dict) -> str:
        """Returns email or combined first/last name."""
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
        """Determines if the account is online or offline."""
        return account_row.get("user_id") is not None


class TaskListItemWidget(QWidget):
    """
    Custom widget for Task items. 
    Includes a completion check, priority badge, and edit button.
    """
    on_check_button_clicked = Signal(object, str, int)
    on_edit_button_clicked = Signal(object, dict)

    CONTENTS_MARGINS_SIZE = QMargins(20, 20, 20, 20)
    SPACING_SIZE = 15
    STRETCH_SIZE = 1

    def __init__(self, task_details: dict, parent=None):
        super().__init__(parent)

        self.task_details = task_details
        layout = QHBoxLayout(self)
        layout.setContentsMargins(TaskListItemWidget.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(TaskListItemWidget.SPACING_SIZE)

        desc_and_title_layout = QVBoxLayout()
        text_and_check_box_layout = QHBoxLayout()

        # Check/Completion button
        title_text = self.task_details.get("title")
        description_text = self.task_details.get("description")
        self.check_btn = PushButton(self)
        self.check_btn.setObjectName("TaskButton")
        self.check_btn.setCheckable(True)
        self.check_btn.clicked.connect(self.checkBtnClicked)
        self.check_btn.setFixedSize(25, 25)

        self.title_label = QLabel(title_text, self)
        self.title_label.setObjectName("TaskTitle")

        # Priority Badge
        task_prio = self.task_details.get("priority")
        self.priority_label_text = self.getPriorityText(task_prio)
        self.priority_label_obj_name = self.getPriorityText(task_prio) #"Low", "Medium", "High"
        self.priority_type_lbl = QLabel(self.priority_label_text, self)
        # The object name is used in QSS to color-code Low/Medium/High
        self.priority_type_lbl.setObjectName(self.priority_label_obj_name)
        self.priority_type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignVCenter)
        self.priority_type_lbl.setFixedSize(70, 30)
        self.priority_type_lbl.setMargin(5)

        self.desc_label = QLabel(description_text, self)
        self.desc_label.setObjectName("TaskDesc")

        self.edit_btn = PushButton(self)
        self.edit_btn.setObjectName("EditButton")
        self.edit_btn.setIcon(QIcon(":/icons/edit.svg"))
        self.edit_btn.clicked.connect(lambda: self.on_edit_button_clicked.emit(self, self.task_details))
        self.edit_btn.setFixedSize(30, 30)

        text_and_check_box_layout.addWidget(self.check_btn)
        text_and_check_box_layout.addWidget(self.title_label)
        text_and_check_box_layout.addWidget(self.priority_type_lbl)

        desc_and_title_layout.addLayout(text_and_check_box_layout)
        desc_and_title_layout.addWidget(self.desc_label)

        layout.addLayout(desc_and_title_layout)
        layout.addStretch(TaskListItemWidget.STRETCH_SIZE)
        layout.addWidget(self.edit_btn)

        # Initialize visual state if task is already complete
        if self.task_details.get("is_complete"):
            self.check_btn.setChecked(True)
            self.toggleCheckedBtn()


    def checkBtnClicked(self):
        """Emits signal to update database and toggles visual strike-out."""
        task_id = self.task_details.get("local_id")
        btn_value = self.check_btn.isChecked()
        self.on_check_button_clicked.emit(self, task_id, btn_value)


    def update(self, priority, description, title):
        """Updates internal data and UI labels after an edit."""
        self.priority_type_lbl.setText(self.getPriorityText(priority))
        self.priority_type_lbl.setObjectName(self.getPriorityText(priority))

        # Refresh stylesheet to apply priority-based color change
        self.window().style_sheet_handler.updateStylesheet()

        self.desc_label.setText(description)
        self.title_label.setText(title)
        self.task_details.update({"priority": priority, "title": title, "description": description})
        # self.task_details["priority"] = priority
        # self.task_details["title"] = title
        # self.task_details["description"] = description


    def toggleCheckedBtn(self):
        """Applies or removes strike-out font effect based on completion status."""
        btn_font = self.title_label.font()
        btn_font.setStrikeOut(self.check_btn.isChecked())
        self.title_label.setFont(btn_font)


    def getPriorityText(self, priority):
        """Maps integer priority levels to display strings."""
        mapping = {
            0: "Low",
            1: "Medium",
            2: "High"
        }
        return mapping.get(priority, "unknown")


class TaskCalendar(QCalendarWidget):
    """
    Customized calendar for task date selection.
    Uses QTextCharFormat to highlight dates containing tasks.
    """
    day_changed = Signal(object)

    def __init__(self, current_day: QDate, parent=None):
        super().__init__(parent)
        self.current_day = current_day
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setGridVisible(True)
        self.setFixedSize(280, 280)

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.ClickFocus)

        # Format for days with existing tasks
        self.task_format = QTextCharFormat()
        self.task_format.setBackground(QBrush(QColor("#2D2926")))
        self.normal_format = QTextCharFormat()

        self.selectionChanged.connect(self.onSelectionChanged)


    def setTaskColor(self, dates_list: list):
        """Applies task highlighting to specific dates."""
        for date in dates_list:
            self.setDateTextFormat(date, self.task_format)


    def clearTaskColor(self, date: QDate):
        """Resets a date to default formatting (e.g., if a task was deleted)."""
        self.setDateTextFormat(date, self.normal_format)


    def onSelectionChanged(self):
        """Emits the new date and hides the popup on selection."""
        self.day_changed.emit(self.selectedDate())
        self.hide()


class FieldStyleManager:
    """Mix-in class to handle error highlighting on form fields."""
    ERROR_STYLE = "QLineEdit { border: 1px solid red; }"
    DEFAULT_STYLE = ""

    def updateEmptyFieldStyle(self, fields: dict):
        """Highlights empty fields and resets filled ones."""
        for field in fields.get("empty"):
            field.setStyleSheet(FieldStyleManager.ERROR_STYLE)
        
        for field in fields.get("filled"):
            field.setStyleSheet(FieldStyleManager.DEFAULT_STYLE)

    def updateInvalidFieldStyle(self, invalid_fields, all_fields):
        """Highlights specific invalid fields based on validation logic."""
        for field in all_fields:
            if field in invalid_fields:
                field.setStyleSheet(FieldStyleManager.ERROR_STYLE)
            else:
                field.setStyleSheet(FieldStyleManager.DEFAULT_STYLE)


class NoTabApplication(QApplication):
    """
    A custom QApplication that disables Tab-key focus navigation 
    globally via an event filter.
    """
    def __init__(self, argv):
        super().__init__(argv)

        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        # Ignore Tab and Backtab key presses to prevent focus jumping
        if event.type() == event.Type.KeyPress:
            if event.key() in [Qt.Key.Key_Tab, Qt.Key.Key_Backtab]:
                return True # Event handled (ignore the key press)
        return super().eventFilter(obj, event)
