from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QCalendarWidget,
    QApplication,
    QFrame,
    QListWidgetItem,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import (
    QIcon,
    QColor,
    QTextCharFormat,
    QBrush,
    QRegularExpressionValidator,
    QPainter,
)
from PySide6.QtCore import (
    QSize,
    QMargins,
    Signal,
    Qt,
    QDate,
    QRegularExpression,
    QRectF
)


class RadioButton(QPushButton):
    """
    Custom button that behaves like a RadioButton.
    Only one instance can be active at a time across the application.
    """
    # Tracks the currently active button across all instances
    active_button = None

    def __init__(self, text: str="", parent: QWidget=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.clicked.connect(self.handle_click)
        self.updateStyle()

    def mousePressEvent(self, event):
        # Prevents unchecking a button by clicking it again once active
        if self.isChecked():
            return 
        super().mousePressEvent(event)

    def handle_click(self):
        """Ensures only one option is active."""
        if RadioButton.active_button and RadioButton.active_button != self:
            RadioButton.active_button.setChecked(False)
            RadioButton.active_button.updateStyle()

        self.setChecked(True)
        RadioButton.active_button = self
        self.updateStyle()

    def updateStyle(self):
        """Changes the cursor to indicate whether the button is interactable."""
        if self.isChecked():
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    @staticmethod
    def resetRadioButtons():
        RadioButton.active_button = None


class PushButton(QPushButton):
    """QPushButton with a pointing hand cursor for better UX."""
    def __init__(self, text: str=None, parent: QWidget=None):
        super().__init__(text, parent)

        self.setCursor(Qt.CursorShape.PointingHandCursor)


class PasswordField(QWidget):
    """
    Composite widget containing a QLineEdit and a toggle button 
    to switch between masked (password) and plain text visibility.
    """
    PASS_VISIBILITY_BTN_SIZE = QSize(40, 40)
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.eye_close_icon = QIcon(":icons/eye_close.svg")
        self.eye_open_icon  = QIcon(":icons/eye_open.svg")

        self.input = QLineEdit(parent=self)
        self.input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_button = QPushButton(parent=self)
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
            self.input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setIcon(self.eye_close_icon)
        else:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setIcon(self.eye_open_icon)


class ClickableLabel(QLabel):
    """A QLabel that behaves like a button, emitting a clicked signal."""
    clicked = Signal()

    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


    def mousePressEvent(self, event):
        self.mouse_pressed = True if event.button() == Qt.MouseButton.LeftButton else False
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        """Emits clicked signal only if the mouse is released inside the label area."""
        if self.mouse_pressed:
            if self.rect().contains(event.position().toPoint()): # Released inside label
                self.clicked.emit()
        self.mouse_pressed = False
        super().mouseReleaseEvent(event)


class FormRow(QWidget):
    """Helper widget that groups a Label and a LineEdit vertically for forms."""
    CONTENTS_MARGINS_SIZE = QMargins(0, 0, 0, 0)

    def __init__(self, label_text: str, input_placeholder_text: str,
                 parent: QWidget, input_max_length: int = None,
                 is_pass_field: bool = False, input_validator_regex: str = None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(FormRow.CONTENTS_MARGINS_SIZE)

        self.label_text = label_text
        self.input_max_length = input_max_length
        self.input_placeholder_text = input_placeholder_text
        self.input_validator_regex = input_validator_regex
        self.error_message = ""

        self.label = QLabel(text=self.label_text, parent=self)
        self.main_layout.addWidget(self.label)

        if is_pass_field:
            self.createPasswordField()
            self.main_layout.addWidget(self.pass_field)
        else:
            self.createNormalField()
            self.main_layout.addWidget(self.input)


    def setErrorMessage(self, error_message):
        self.error_message = error_message


    def updateError(self, input_field: QLineEdit, error_message: str):
        ERROR_STYLE = "QLineEdit { border: 1px solid red; }"
        DEFAULT_STYLE = ""

        # if errors are similar return
        if self.error_message == error_message:
            return

        # if an error label already exist remove it
        if hasattr(self, "error_label"):
            self.error_label.deleteLater()
            del self.error_label

        # if error_message is not empty(error occured)
        if error_message: 
            input_field.setStyleSheet(ERROR_STYLE)
            self.error_label = QLabel(error_message, wordWrap=True, parent=self)
            self.error_label.setObjectName("ErrorMessage")
            self.main_layout.addWidget(self.error_label)
        #otherwise remove error
        else:
            input_field.setStyleSheet(DEFAULT_STYLE)

        self.setErrorMessage(error_message)


    def createPasswordField(self):
        self.pass_field = PasswordField(self)
        self.pass_field.input.setPlaceholderText(self.input_placeholder_text)
        if self.input_max_length:
            self.pass_field.input.setMaxLength(self.input_max_length)


    def createNormalField(self):
        self.input = QLineEdit(self)
        self.input.setPlaceholderText(self.input_placeholder_text)

        if self.input_max_length:
            self.input.setMaxLength(self.input_max_length)

        if self.input_validator_regex:
            self.input.setValidator(QRegularExpressionValidator(QRegularExpression(self.input_validator_regex)))


class AccountListItemWidget(QWidget):
    """Custom widget for account selection list items, showing user info and account type."""
    def __init__(self, widget_item: QListWidgetItem, parent: QWidget):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        text_layout = QVBoxLayout()
        self.account_details = widget_item.data(Qt.ItemDataRole.UserRole)

        title_text = self.formatTitle()
        subtitle_text = self.formatSubtitle()

        self.title_label = QLabel(text=title_text, wordWrap=True, parent=self)
        self.title_label.setObjectName("ItemTitle")

        self.sub_label = QLabel(text=subtitle_text, wordWrap=True ,parent=self)
        self.sub_label.setObjectName("ItemSub")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.sub_label)

        layout.addLayout(text_layout)

        # Logic to display "Online" vs "Offline" badge
        acc_type_label_txt = "Online" if self.isOnlineAccount() else "Offline"
        acc_type_label_obj_name = "onlineLabel" if self.isOnlineAccount() else "offlineLabel"

        self.acc_type_lbl = QLabel(text=acc_type_label_txt, parent=self)
        self.acc_type_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.acc_type_lbl.setObjectName(acc_type_label_obj_name)
        self.acc_type_lbl.setFixedSize(50, 30)
        self.acc_type_lbl.setMargin(5)
        layout.addWidget(self.acc_type_lbl)


    def formatTitle(self) -> str:
        """Returns nickname or a fallback ID-based string."""
        nickname = self.account_details.get("nickname")
        if nickname:
            return nickname
        return f"Account #{self.account_details.get('id', '?')}"


    def formatSubtitle(self) -> str:
        """Returns email or combined first/last name."""
        email = self.account_details.get("email")
        f_name = self.account_details.get("f_name")
        l_name = self.account_details.get("l_name")
        if email:
            return email
        name_parts = [part for part in [f_name, l_name] if part]
        if name_parts:
            return " ".join(name_parts)
        return f"ID: {self.account_details.get('id', '?')}"


    def isOnlineAccount(self) -> bool:
        """Determines if the account is online or offline."""
        return self.account_details.get("user_id") is not None


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

    def __init__(self, task_details: dict, parent: QWidget=None):
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
        self.check_btn = PushButton(parent=self)
        self.check_btn.setObjectName("TaskButton")
        self.check_btn.setCheckable(True)
        self.check_btn.clicked.connect(self.checkBtnClicked)
        self.check_btn.setFixedSize(25, 25)

        self.title_label = QLabel(text=title_text, parent=self)
        self.title_label.setObjectName("TaskTitle")

        # Priority Badge
        task_prio = self.task_details.get("priority")
        self.priority_label_text = self.getPriorityText(task_prio)
        self.priority_label_obj_name = self.getPriorityText(task_prio) #"Low", "Medium", "High"
        self.priority_type_lbl = QLabel(text=self.priority_label_text, parent=self)
        # The object name is used in QSS to color-code Low/Medium/High
        self.priority_type_lbl.setObjectName(self.priority_label_obj_name)
        self.priority_type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.priority_type_lbl.setFixedSize(70, 30)
        self.priority_type_lbl.setMargin(5)

        self.desc_label = QLabel(text=description_text, parent=self)
        self.desc_label.setObjectName("TaskDesc")

        self.edit_btn = PushButton(parent=self)
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

    def __init__(self, current_day: QDate, parent: QWidget):
        super().__init__(parent)
        self.current_day = current_day
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(True)
        self.setFixedSize(280, 280)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

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


class HabitListItemWidget(QWidget):
    on_edit_button_clicked = Signal(object, dict)

    CONTENTS_MARGINS_SIZE = QMargins(20, 20, 20, 20)
    SPACING_SIZE = 15
    STRETCH_SIZE = 1

    def __init__(self, habit_details: dict, parent: QWidget=None):
        super().__init__(parent)
        self.button_list = []
        self.habit_details = habit_details
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(TaskListItemWidget.CONTENTS_MARGINS_SIZE)
        self.layout.setSpacing(TaskListItemWidget.SPACING_SIZE)
        self.current_date = QDate.currentDate()

        # Check/Completion button
        title_text = self.habit_details.get("title")

        self.title_label = QLabel(text=title_text, parent=self)
        self.title_label.setObjectName("HabitTitle")

        # Priority Badge
        task_prio = self.habit_details.get("priority")
        self.priority_label_text = self.getPriorityText(task_prio)
        self.priority_label_obj_name = self.getPriorityText(task_prio) #"Low", "Medium", "High"
        self.priority_type_lbl = QLabel(text=self.priority_label_text, parent=self)
        # The object name is used in QSS to color-code Low/Medium/High
        self.priority_type_lbl.setObjectName(self.priority_label_obj_name)
        self.priority_type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignVCenter)
        self.priority_type_lbl.setFixedSize(70, 30)
        self.priority_type_lbl.setMargin(5)

        self.edit_btn = PushButton(parent=self)
        self.edit_btn.setObjectName("EditButton")
        self.edit_btn.setIcon(QIcon(":/icons/edit.svg"))
        self.edit_btn.clicked.connect(lambda: self.on_edit_button_clicked.emit(self, self.habit_details))
        self.edit_btn.setFixedSize(30, 30)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.priority_type_lbl)
        self.layout.addStretch(HabitListItemWidget.STRETCH_SIZE)
        self.layout.addWidget(self.edit_btn)

        self.addHabitButtons()


    def addHabitButtons(self):
        for i in range(-4, 1, 1):
            btn = HabitButton(self, self.current_date.addDays(i), self.habit_details)
            self.button_list.append(btn)
            self.layout.addWidget(btn)


    def update(self, habit_details: dict):
        """Updates internal data and UI labels after an edit."""
        title = habit_details.get("title")
        priority = habit_details.get("priority")
        self.priority_type_lbl.setText(self.getPriorityText(priority))
        self.priority_type_lbl.setObjectName(self.getPriorityText(priority))

        # Refresh stylesheet to apply priority-based color change
        self.window().style_sheet_handler.updateStylesheet()

        self.title_label.setText(title)
        self.habit_details.update({"priority": priority,
                                   "title": title,
                                   "description": habit_details.get("description"),
                                   "color": habit_details.get("color"),
                                   "question": habit_details.get("question"),
                                   "target": habit_details.get("target"),
                                   "unit": habit_details.get("unit")
                                   })


    def getPriorityText(self, priority):
        """Maps integer priority levels to display strings."""
        mapping = {
            0: "Low",
            1: "Medium",
            2: "High"
        }
        return mapping.get(priority, "unknown")


class HabitButton(QPushButton):
    on_habit_button_clicked = Signal(object, object, dict, dict)
    def __init__(self, parent: QWidget, date: QDate, habit_deatils: dict, daily_habit_details: dict = {}):
        super().__init__(parent)
        self.date = date
        self.habit_details = habit_deatils
        self.daily_habit_details = daily_habit_details
        self.setFixedSize(80, 80)
        self.setObjName("HabitButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(
            lambda: self.on_habit_button_clicked.emit(self,
                                                      self.date,
                                                      self.habit_details,
                                                      self.daily_habit_details)
            )


    def setObjName(self, object_name: str = "HabitButton"):
        self.setObjectName(object_name)


class ColorPicker(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("ColorPicker")
        self.main_layout = QHBoxLayout(self)
        self.color = "blue"

        self.color_main = QPushButton(parent=self)
        self.color_main.setObjectName("MainColorBlue")
        self.main_layout.addWidget(self.color_main)
        self.main_layout.addStretch(1)

        self.blue_color = PushButton(parent=self)
        self.blue_color.setObjectName("BlueColor")
        self.blue_color.clicked.connect(lambda: self.changeColor("blue"))
        self.main_layout.addWidget(self.blue_color)

        self.red_color = PushButton(parent=self)
        self.red_color.setObjectName("RedColor")
        self.red_color.clicked.connect(lambda: self.changeColor("red"))
        self.main_layout.addWidget(self.red_color)

        self.green_color = PushButton(parent=self)
        self.green_color.setObjectName("GreenColor")
        self.green_color.clicked.connect(lambda: self.changeColor("green"))
        self.main_layout.addWidget(self.green_color)

        self.yellow_color = PushButton(parent=self)
        self.yellow_color.setObjectName("YellowColor")
        self.yellow_color.clicked.connect(lambda: self.changeColor("yellow"))
        self.main_layout.addWidget(self.yellow_color)

        self.purple_color = PushButton(parent=self)
        self.purple_color.setObjectName("PurpleColor")
        self.purple_color.clicked.connect(lambda: self.changeColor("purple"))
        self.main_layout.addWidget(self.purple_color)

        self.cyan_color = PushButton(parent=self)
        self.cyan_color.setObjectName("CyanColor")
        self.cyan_color.clicked.connect(lambda: self.changeColor("cyan"))
        self.main_layout.addWidget(self.cyan_color)


    def changeColor(self, color: str):
        self.color_main.setObjectName(f"MainColor{color.title()}")
        self.window().style_sheet_handler.updateStylesheet()
        self.color = color


    def getColor(self):
        return self.color


class AccountDetailsFrame(QFrame):
    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        first_name_text = account_details.get("f_name")
        last_name_text   = account_details.get("l_name")
        nickname_text   = account_details.get("nickname")

        layout = QVBoxLayout(self)

        f_name_layout = QHBoxLayout()
        f_name_label   = QLabel(text="First name :", parent=self)
        f_name_label.setObjectName("Label")
        f_name_text_label = QLabel(text=first_name_text, parent=self)
        f_name_layout.addWidget(f_name_label)
        f_name_layout.addWidget(f_name_text_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(f_name_layout)

        l_name_layout = QHBoxLayout()
        l_name_label   = QLabel(text="Last name :", parent=self)
        l_name_text_label = QLabel(text=last_name_text, parent=self)
        l_name_layout.addWidget(l_name_label)
        l_name_label.setObjectName("Label")
        l_name_layout.addWidget(l_name_text_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(l_name_layout)

        nickname_layout = QHBoxLayout()
        nickname_label = QLabel(text="nickname  :", parent=self)
        nickname_label.setObjectName("Label")
        nickname_text_label = QLabel(text=nickname_text, parent=self)
        nickname_layout.addWidget(nickname_label)
        nickname_layout.addWidget(nickname_text_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(nickname_layout)

        layout.addSpacerItem(QSpacerItem(20, 20))
        self.logout_btn = PushButton("Logout", parent=self)
        self.logout_btn.setFixedSize(90, 30)
        self.logout_btn.clicked.connect(lambda: self.hide())
        layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class ScalableSvgWidget(QSvgWidget):
    def __init__(self, svg_path: str, parent: QWidget):
        super().__init__(svg_path, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def paintEvent(self, event):
        """Override paint event to maintain aspect ratio"""
        if self.renderer().isValid():
            painter = QPainter(self)
            renderer = self.renderer()
            
            # Calculate scaled size preserving aspect ratio
            svg_size = renderer.defaultSize()
            widget_size = self.size()
            
            # Scale to fit
            svg_aspect = svg_size.width() / svg_size.height()
            widget_aspect = widget_size.width() / widget_size.height()
            
            if svg_aspect > widget_aspect:
                width = widget_size.width()
                height = width / svg_aspect
            else:
                height = widget_size.height()
                width = height * svg_aspect
            
            # Center the image
            x = (widget_size.width() - width) / 2
            y = (widget_size.height() - height) / 2
            
            renderer.render(painter, QRectF(x, y, width, height))

            painter.end()


class HabitDetailsCalendar(QCalendarWidget):
    habit_already_exist_signal = Signal(object, dict)
    habit_doesnt_exist_signal = Signal(object)

    def __init__(self, habit_details: dict, daily_habits_map: dict, parent: QWidget):
        super().__init__(parent)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(True)
        self.setMaximumDate(QDate.currentDate())
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.habit_details = habit_details
        self.daily_habits_map = daily_habits_map
        self.daily_habit_format = QTextCharFormat()
        self.daily_habit_format.setFontItalic(True)
        self.normal_format = QTextCharFormat()

        self.clicked.connect(self.daySelected)
        self.initHabitsDetailColor()


    def applyColorToTextFormat(self, value: int):
        habit_color = self.habit_details.get("color")
        habit_target = self.habit_details.get("target")

        color_name = f"{habit_color.title()}Color" if value >= habit_target else f"Lesser{habit_color.title()}Color"

        color_map = {
            "BlueColor":         QBrush(QColor("#0E34A7")),
            "RedColor":          QBrush(QColor("#8B1E3F")),
            "GreenColor":        QBrush(QColor("#006633")),
            "YellowColor":       QBrush(QColor("#FFCC00")),
            "PurpleColor":       QBrush(QColor("#621b94")),
            "CyanColor":         QBrush(QColor("#009999")),
            "LesserBlueColor":   QBrush(QColor("#3A4F7A")),
            "LesserRedColor":    QBrush(QColor("#8B354F")),
            "LesserGreenColor":  QBrush(QColor("#4a8c6b")),
            "LesserYellowColor": QBrush(QColor("#e1c360")),
            "LesserPurpleColor": QBrush(QColor("#9d64c5")),
            "LesserCyanColor":   QBrush(QColor("#5ccbcb")),
        }
        self.daily_habit_format.setBackground(color_map.get(color_name))


    def initHabitsDetailColor(self):
        for details in self.daily_habits_map.values():
            date = QDate().fromString(details.get("date"), Qt.DateFormat.ISODate)
            value = details.get("value")

            self.applyColorToTextFormat(value=value)
            self.setDateTextFormat(date, self.daily_habit_format)


    def daySelected(self, clicked_date:QDate):
        selected_date_details = self.daily_habits_map.get(clicked_date)
        if selected_date_details:
            self.habit_already_exist_signal.emit(clicked_date,  selected_date_details)
        else:
            self.habit_doesnt_exist_signal.emit(clicked_date)


    def colorDay(self, date: QDate, value: int):
        iso_date_format= QDate.fromString(date, Qt.DateFormat.ISODate)

        self.applyColorToTextFormat(value=value)
        self.setDateTextFormat(iso_date_format, self.daily_habit_format)


    def clearColorDay(self, date: QDate):
        self.setDateTextFormat(date, self.normal_format)


    def updateDailyHabitMap(self, daily_habit_map: dict):
        self.daily_habits_map = daily_habit_map
