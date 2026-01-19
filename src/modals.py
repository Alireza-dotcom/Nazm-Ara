from widgets import (
    PushButton,
    FieldStyleManager,
    ColorPicker,
    FormRow,
    TaskListItemWidget,
    HabitListItemWidget,
    HabitButton
)
from form_processor import FormProcessor
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QWidget,
    
)

from PySide6.QtCore import Qt, QRect, QEvent, Signal, QDate


class AddTaskModal(QFrame):
    add_task_clicked = Signal(dict)
    on_delete_clicked = Signal(object, str)
    on_update_clicked = Signal(object, dict, str)

    STRETCH_SIZE = 1
    MEDIUM_INDEX = 1
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget, task_object: TaskListItemWidget, task_details: dict = None):
        # The 'shield' acts as a semi-transparent overlay covering the parent window
        # to block interactions and serve as a background for the modal.
        self.main_win = parent.window()
        self.shield = QFrame(self.main_win)
        self.shield.setObjectName("shield")

        super().__init__(self.shield)
        self.setObjectName("AddTaskModal")
        self.shield.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.task_details = task_details
        self.task_object = task_object

        self.form_processor = FormProcessor(parent=self)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_exit_layout = QHBoxLayout()
        create_task_lbl = QLabel(text="Create task", parent=self)
        create_task_lbl.setObjectName("TitleLabel")
        title_exit_layout.addWidget(create_task_lbl)
        title_exit_layout.addStretch(AddTaskModal.STRETCH_SIZE)

        close_btn = PushButton(parent=self)
        close_btn.setObjectName("CloseButton")
        close_btn.setIcon(QIcon(":icons/cross.svg"))
        close_btn.clicked.connect(self.shield.close)
        title_exit_layout.addWidget(close_btn)
        layout.addLayout(title_exit_layout)

        self.task_name = FormRow(label_text=f"Task name{AddTaskModal.REQUIRED_FIELD}",
                             input_placeholder_text="e.g. Add feature X to project",
                             input_max_length=70,
                             parent=self)
        layout.addWidget(self.task_name)

        self.description = FormRow(label_text="Description",
                             input_placeholder_text="(Optional)",
                             input_max_length=70,
                             parent=self)
        layout.addWidget(self.description)

        priority_lbl = QLabel(text="Priority", parent=self)
        layout.addWidget(priority_lbl)
        self.priority_item = QComboBox(self)
        self.addPriorityItems()
        self.priority_item.setCurrentIndex(AddTaskModal.MEDIUM_INDEX)
        layout.addWidget(self.priority_item)
        layout.addStretch(AddTaskModal.STRETCH_SIZE)

        # If task_details is not provided, open modal in create mode;
        # otherwise, open in edit mode.
        if not self.task_details:
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)
            layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            buttons_layout = QHBoxLayout()
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)

            self.delete_btn = PushButton(text="Delete", parent=self)
            self.delete_btn.setObjectName("DeleteButton")
            self.delete_btn.clicked.connect(self.onDeleteClicked)
            buttons_layout.addWidget(self.delete_btn)
            buttons_layout.addStretch(AddTaskModal.STRETCH_SIZE)
            buttons_layout.addWidget(self.save_btn)

            layout.addLayout(buttons_layout)
            self.initialFields()

        # Listen to Main Window for Resizing
        # Installs an event filter so this widget can react when the main window is resized
        self.main_win.installEventFilter(self)
        
        self.shield.show()
        self.show()
        self.applyResizeLogic()


    def initialFields(self):
        """Populates fields with existing data when in edit mode."""
        self.task_name.input.setText(self.task_details.get("title"))
        self.description.input.setText(self.task_details.get("description"))
        self.priority_item.setCurrentIndex(self.task_details.get("priority"))


    def onDeleteClicked(self):
        self.on_delete_clicked.emit(self.task_object, self.task_details.get("local_id"))
        self.shield.close()


    def eventFilter(self, obj, event):
        # Keeps the modal centered if the user resizes the main application window
        if obj == self.main_win and event.type() == QEvent.Type.Resize:
            self.applyResizeLogic()
        return super().eventFilter(obj, event)


    def addPriorityItems(self):
        """Adds priority items into QComboBox"""
        items = ["Low", "Medium", "High"]
        for item in items:
            self.priority_item.addItem(item)


    def applyResizeLogic(self):
        """Re-calculates position to keep the modal centered within the parent window."""
        self.shield.setGeometry(self.main_win.rect())
        
        width = 400
        height = 400

        p_rect = self.shield.rect()
        
        x = (p_rect.width() - width) // 2
        y = (p_rect.height() - height) // 2
        
        self.setGeometry(QRect(int(x), int(y), int(width), int(height)))


    def onSaveClicked(self):
        """Checks the validation process before emitting the (update or add) signal."""
        field_map = [
            {"field_name": "title",       "field_input":  self.task_name.input,   "field_object": self.task_name,   "is_optional": False},
            {"field_name": "description", "field_input":  self.description.input, "field_object": self.description, "is_optional": True },
            {"field_name": "priority",    "field_object": self.priority_item},
        ]

        data = self.form_processor.taskModalValidator(field_map)
        if not data:
            return

        # Emit appropriate signal based on whether we are updating an existing item or adding a new one
        if self.task_details:
            task_id = self.task_details.get("local_id")
            self.on_update_clicked.emit(self.task_object, data, task_id)
        else:
            self.add_task_clicked.emit(data)

        self.shield.close()


class AddHabitModal(QFrame):
    add_habit_clicked = Signal(dict)
    on_delete_clicked = Signal(object, str)
    on_update_clicked = Signal(object, dict, str)

    STRETCH_SIZE = 1
    MEDIUM_INDEX = 1
    CONTENT_SPACING = 5
    REQUIRED_FIELD = "<span style='color: red; font-size: 15px'>*</span>"

    def __init__(self, parent: QWidget, habit_object: HabitListItemWidget, habit_details: dict = None):
        self.main_win = parent.window()
        self.shield = QFrame(self.main_win)
        self.shield.setObjectName("shield")

        super().__init__(self.shield)
        self.setObjectName("AddHabitModal")
        self.shield.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.habit_details = habit_details
        self.habit_object = habit_object

        self.form_processor = FormProcessor(parent=self)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(AddHabitModal.CONTENT_SPACING)

        title_exit_layout = QHBoxLayout()
        create_task_lbl = QLabel(text="Create habit", parent=self)
        create_task_lbl.setObjectName("TitleLabel")
        title_exit_layout.addWidget(create_task_lbl)
        title_exit_layout.addStretch(AddHabitModal.STRETCH_SIZE)

        close_btn = PushButton(parent=self)
        close_btn.setObjectName("CloseButton")
        close_btn.setIcon(QIcon(":icons/cross.svg"))
        close_btn.clicked.connect(self.shield.close)
        title_exit_layout.addWidget(close_btn)
        layout.addLayout(title_exit_layout)

        self.habit_name = FormRow(label_text=f"Habit name{AddTaskModal.REQUIRED_FIELD}",
                             input_placeholder_text="e.g. Reading book",
                             input_max_length=50,
                             parent=self)
        layout.addWidget(self.habit_name)

        self.question = FormRow(label_text=f"Question{AddTaskModal.REQUIRED_FIELD}",
                             input_placeholder_text="e.g. Linux Bible",
                             input_max_length=50,
                             parent=self)
        layout.addWidget(self.question)

        self.unit = FormRow(label_text=f"Unit{AddTaskModal.REQUIRED_FIELD}",
                             input_placeholder_text="e.g. page",
                             input_max_length=25,
                             parent=self)
        layout.addWidget(self.unit)

        self.target = FormRow(label_text=f"Target{AddTaskModal.REQUIRED_FIELD}",
                             input_placeholder_text="e.g. 20",
                             input_max_length=30,
                             input_validator_regex="^[\d]+$",
                             parent=self)
        layout.addWidget(self.target)

        unit_target_layout = QHBoxLayout()
        unit_target_layout.addWidget(self.unit)
        unit_target_layout.addWidget(self.target)
        layout.addLayout(unit_target_layout)

        self.description = FormRow(label_text="Description",
                             input_placeholder_text="(Optional)",
                             input_max_length=50,
                             parent=self)
        layout.addWidget(self.description)

        priority_lbl = QLabel(text="Priority", parent=self)
        layout.addWidget(priority_lbl)
        self.priority_item = QComboBox(self)
        self.addPriorityItems()
        self.priority_item.setCurrentIndex(AddHabitModal.MEDIUM_INDEX)
        layout.addWidget(self.priority_item)

        color_lbl = QLabel(text="Color", parent=self)
        layout.addWidget(color_lbl)
        self.color_picker = ColorPicker(self)
        layout.addWidget(self.color_picker)
        layout.addStretch(AddHabitModal.STRETCH_SIZE)

        # If habit_details is not provided, open modal in create mode;
        # otherwise, open in edit mode.
        if not self.habit_details:
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)
            layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            buttons_layout = QHBoxLayout()
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)

            self.delete_btn = PushButton(text="Delete", parent=self)
            self.delete_btn.setObjectName("DeleteButton")
            self.delete_btn.clicked.connect(self.onDeleteClicked)
            buttons_layout.addWidget(self.delete_btn)
            buttons_layout.addStretch(AddHabitModal.STRETCH_SIZE)
            buttons_layout.addWidget(self.save_btn)

            layout.addLayout(buttons_layout)
            self.initialFields()

        # Listen to Main Window for Resizing
        # Installs an event filter so this widget can react when the main window is resized
        self.main_win.installEventFilter(self)
        
        self.shield.show()
        self.show()
        self.applyResizeLogic()


    def initialFields(self):
        """Populates fields with existing data when in edit mode."""
        self.habit_name.input.setText(self.habit_details.get("title"))
        self.question.input.setText(self.habit_details.get("question"))
        self.unit.input.setText(str(self.habit_details.get("unit")))
        self.target.input.setText(str(self.habit_details.get("target")))
        self.description.input.setText(self.habit_details.get("description"))
        self.priority_item.setCurrentIndex(self.habit_details.get("priority"))
        self.color_picker.changeColor(self.habit_details.get("color"))


    def onDeleteClicked(self):
        self.on_delete_clicked.emit(self.habit_object, self.habit_details.get("local_id"))
        self.shield.close()


    def eventFilter(self, obj, event):
        # Keeps the modal centered if the user resizes the main application window
        if obj == self.main_win and event.type() == QEvent.Type.Resize:
            self.applyResizeLogic()
        return super().eventFilter(obj, event)


    def addPriorityItems(self):
        """Adds priority items into QComboBox"""
        items = ["Low", "Medium", "High"]
        for item in items:
            self.priority_item.addItem(item)


    def applyResizeLogic(self):
        """Re-calculates position to keep the modal centered within the parent window."""
        self.shield.setGeometry(self.main_win.rect())
        
        width = 500
        height = 650

        p_rect = self.shield.rect()
        
        x = (p_rect.width() - width) // 2
        y = (p_rect.height() - height) // 2
        
        self.setGeometry(QRect(int(x), int(y), int(width), int(height)))


    def onSaveClicked(self):
        """Checks the validation process before emitting the (update or add) signal."""
        field_map = [
            {"field_name": "title",       "field_input":  self.habit_name.input,  "field_object": self.habit_name, "is_optional": False},
            {"field_name": "question",    "field_input":  self.question.input,    "field_object": self.question,   "is_optional": False},
            {"field_name": "unit",        "field_input":  self.unit.input,        "field_object": self.unit,       "is_optional": False},
            {"field_name": "target",      "field_input":  self.target.input,      "field_object": self.target,     "is_optional": False},
            {"field_name": "description", "field_input":  self.description.input, "field_object": self.description,"is_optional": True },
            {"field_name": "priority",    "field_object": self.priority_item},
            {"field_name": "color",       "field_object": self.color_picker},
        ]

        data = self.form_processor.habitModalValidator(field_map)
        if not data:
            return

        # Emit appropriate signal based on whether we are updating an existing item or adding a new one
        if self.habit_details:
            task_id = self.habit_details.get("local_id")
            self.on_update_clicked.emit(self.habit_object, data, task_id)
        else:
            self.add_habit_clicked.emit(data)

        self.shield.close()


class AddDailyHabitModal(QFrame):
    add_daily_habit_clicked = Signal(object, dict)
    on_delete_clicked = Signal(object, int)
    on_update_clicked = Signal(object, dict)

    STRETCH_SIZE = 1
    MEDIUM_INDEX = 1
    CONTENT_SPACING = 20

    def __init__(self, parent: QWidget, date: QDate ,habit_button: HabitButton, habit_details: dict, daily_habit_details: dict = None):
        self.main_win = parent.window()
        self.shield = QFrame(self.main_win)
        self.shield.setObjectName("shield")

        super().__init__(self.shield)
        self.setObjectName("AddDailyHabitModal")
        self.shield.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.date = date
        self.habit_details = habit_details
        self.habit_button = habit_button
        self.daily_habit_details = daily_habit_details
        self.question = habit_details.get("question")
        self.unit = habit_details.get("unit")

        self.form_processor = FormProcessor(parent=self)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(AddDailyHabitModal.CONTENT_SPACING)

        title_exit_layout = QHBoxLayout()
        create_task_lbl = QLabel(text=self.date.toString("ddd d"), parent=self)
        create_task_lbl.setObjectName("TitleLabel")
        title_exit_layout.addWidget(create_task_lbl)
        title_exit_layout.addStretch(AddDailyHabitModal.STRETCH_SIZE)

        close_btn = PushButton(parent=self)
        close_btn.setObjectName("CloseButton")
        close_btn.setIcon(QIcon(":icons/cross.svg"))
        close_btn.clicked.connect(self.shield.close)
        title_exit_layout.addWidget(close_btn)
        layout.addLayout(title_exit_layout)

        value_input_unit_layout = QHBoxLayout()
        self.value = FormRow(label_text=str(self.question),
                             input_placeholder_text=str(self.unit),
                             input_max_length=25,
                             input_validator_regex="^[\d]+$",
                             parent=self)
        value_input_unit_layout.addWidget(self.value)


        layout.addLayout(value_input_unit_layout)
        layout.addStretch(AddDailyHabitModal.STRETCH_SIZE)
        # If daily_habit_details is not provided, open modal in create mode;
        # otherwise, open in edit mode.
        if not self.daily_habit_details:
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)
            layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            buttons_layout = QHBoxLayout()
            self.save_btn = PushButton(text="Save", parent=self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)

            self.delete_btn = PushButton(text="Delete", parent=self)
            self.delete_btn.setObjectName("DeleteButton")
            self.delete_btn.clicked.connect(self.onDeleteClicked)
            buttons_layout.addWidget(self.delete_btn)
            buttons_layout.addStretch(AddHabitModal.STRETCH_SIZE)
            buttons_layout.addWidget(self.save_btn)

            layout.addLayout(buttons_layout)
            self.initialFields()

        # Listen to Main Window for Resizing
        # Installs an event filter so this widget can react when the main window is resized
        self.main_win.installEventFilter(self)
        
        self.shield.show()
        self.show()
        self.applyResizeLogic()


    def applyResizeLogic(self):
        """Re-calculates position to keep the modal centered within the parent window."""
        self.shield.setGeometry(self.main_win.rect())
        
        width = 500
        height = 250

        p_rect = self.shield.rect()
        
        x = (p_rect.width() - width) // 2
        y = (p_rect.height() - height) // 2
        
        self.setGeometry(QRect(int(x), int(y), int(width), int(height)))


    def eventFilter(self, obj, event):
        # Keeps the modal centered if the user resizes the main application window
        if obj == self.main_win and event.type() == QEvent.Type.Resize:
            self.applyResizeLogic()
        return super().eventFilter(obj, event)


    def initialFields(self):
        """Populates value field with existing data when in edit mode."""
        self.value.input.setText(str(self.daily_habit_details.get("value")))
        self.value.label.setText(str(self.habit_details.get("question")))


    def onDeleteClicked(self):
        id =  self.daily_habit_details.get("local_id")
        self.on_delete_clicked.emit(self.habit_button, id)
        self.shield.close()


    def onSaveClicked(self):
        """Checks the validation process before emitting the (update or add) signal."""
        field_map = [
            {"field_name": "value", "field_input": self.value.input, "field_object": self.value, "is_optional": False},
        ]

        data = self.form_processor.dailyHabitModalValidator(field_map)
        if not data:
            return

        # add req field to change the database and buttons color
        data.update({"habit_id": self.habit_details.get("local_id"),
                        "user_id": self.habit_details.get("user_id"),
                        "date": self.date.toString(Qt.DateFormat.ISODate),
                        "color": self.habit_details.get("color"),
                        "target": self.habit_details.get("target"),
                        "value": int(data.get("value")),
                        })

        # Emit appropriate signal based on whether we are updating an existing item or adding a new one
        if self.daily_habit_details:
            data.update({"local_id": self.daily_habit_details["local_id"]})
            self.on_update_clicked.emit(self.habit_button, data)
        else:
            self.add_daily_habit_clicked.emit(self.habit_button, data)

        self.shield.close()
