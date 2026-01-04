from widgets import PushButton, FieldStyleManager
from form_processor import FormProcessor
from notification_handler import NotificationHandler
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QComboBox
)
from PySide6.QtCore import Qt, QRect, QEvent, Signal

class AddTodoModal(QFrame, FieldStyleManager):
    add_todo_clicked = Signal(dict)
    on_delete_clicked = Signal(object, str)
    on_update_clicked = Signal(str ,dict, object)

    STRETCH_SIZE = 1
    MEDIUM_INDEX = 1

    def __init__(self, parent, task_object, todo_details: dict = None):
        self.main_win = parent.window()
        self.shield = QFrame(self.main_win)
        self.shield.setObjectName("shield")

        super().__init__(self.shield)
        self.setObjectName("AddTodoModal")
        self.shield.setAttribute(Qt.WA_DeleteOnClose)
        self.todo_details = todo_details
        self.task_object = task_object

        self.form_processor = FormProcessor()
        self.notification_handler = NotificationHandler()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_exit_layout = QHBoxLayout()
        create_task_lbl = QLabel("Create task", self)
        create_task_lbl.setObjectName("TitleLabel")
        title_exit_layout.addWidget(create_task_lbl)
        title_exit_layout.addStretch(AddTodoModal.STRETCH_SIZE)

        close_btn = PushButton(parent=self)
        close_btn.setObjectName("CloseButton")
        close_btn.setIcon(QIcon(":icons/cross.svg"))
        close_btn.clicked.connect(self.shield.close)
        title_exit_layout.addWidget(close_btn)
        layout.addLayout(title_exit_layout)

        task_name_lbl = QLabel("Task name", self)
        layout.addWidget(task_name_lbl)
        self.task_name_input = QLineEdit(self)
        self.task_name_input.setMaxLength(50)
        layout.addWidget(self.task_name_input)


        description_lbl = QLabel("Description", self)
        layout.addWidget(description_lbl)
        self.description_input = QLineEdit(self)
        self.description_input.setMaxLength(50)
        layout.addWidget(self.description_input)

        priority_lbl = QLabel("Priority", self)
        layout.addWidget(priority_lbl)
        self.priority_item = QComboBox(self)
        self.addPiorityItems()
        self.priority_item.setCurrentIndex(AddTodoModal.MEDIUM_INDEX)
        layout.addWidget(self.priority_item)
        layout.addStretch(AddTodoModal.STRETCH_SIZE)

        if not self.todo_details:
            self.save_btn = PushButton("Save", self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)
            layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            buttons_layout = QHBoxLayout()
            self.save_btn = PushButton("Save", self)
            self.save_btn.setObjectName("SaveButton")
            self.save_btn.clicked.connect(self.onSaveClicked)

            self.delete_btn = PushButton("Delete", self)
            self.delete_btn.setObjectName("DeleteButton")
            self.delete_btn.clicked.connect(self.onDeleteClicked)
            buttons_layout.addWidget(self.delete_btn)
            buttons_layout.addStretch(AddTodoModal.STRETCH_SIZE)
            buttons_layout.addWidget(self.save_btn)

            layout.addLayout(buttons_layout)
            self.initialFields()

        # Listen to Main Window for Resizing
        self.main_win.installEventFilter(self)
        
        self.shield.show()
        self.show()
        self.applyResizeLogic()


    def initialFields(self):
        self.task_name_input.setText(self.todo_details.get("title"))
        self.description_input.setText(self.todo_details.get("description"))
        self.priority_item.setCurrentIndex(self.todo_details.get("priority"))


    def onDeleteClicked(self):
        self.on_delete_clicked.emit(self.task_object, self.todo_details["local_id"])
        self.shield.close()


    def eventFilter(self, obj, event):
        if obj == self.main_win and event.type() == QEvent.Resize:
            self.applyResizeLogic()
        return super().eventFilter(obj, event)


    def addPiorityItems(self):
        items = ["Low", "Medium", "High"]
        for item in items:
            self.priority_item.addItem(item)


    def applyResizeLogic(self):
        self.shield.setGeometry(self.main_win.rect())
        
        width = 400
        height = 500

        p_rect = self.shield.rect()
        
        x = (p_rect.width() - width) // 2
        y = (p_rect.height() - height) // 2
        
        self.setGeometry(QRect(int(x), int(y), int(width), int(height)))


    def onSaveClicked(self):
        field_map = {
            "title": self.task_name_input,
            "description": self.description_input,
            "priority": self.priority_item
        }

        if not self.handleEmptyValidation(field_map.copy()):
            return
        
        is_valid, data = self.handleFormatValidation(field_map)
        if not is_valid:
            return 

        if self.todo_details:
            todo_id = self.todo_details.get("local_id")
            self.on_update_clicked.emit(todo_id, data, self.task_object)
        else:
            self.add_todo_clicked.emit(data)

        self.shield.close()


    def handleEmptyValidation(self, field_map:dict):
        field_map.pop("priority")
        form_fields = list(field_map.values())
        field_status = self.form_processor.findEmptyAndFilledFields(form_fields)
        
        self.updateEmptyFieldStyle(field_status)
        
        if field_status["empty"]:
            self.notification_handler.showToast(
                "bottom_right", "Empty fields",
                "Please fill in all required fields.", "error", duration=5000
            )
            return False
        return True


    def handleFormatValidation(self, field_map):
        is_valid, result = self.form_processor.getTodoModalsValidationErros(field_map)
        
        if not is_valid:
            form_fields = list(field_map.values())
            self.updateInvalidFieldStyle(result["invalid_widgets"], form_fields)
            
            errors = "\n".join(result["errors"])
            duration = max(4000, len(errors) * 50)
            
            self.notification_handler.showToast(
                "bottom_right", "Validation Errors",
                errors, "error", duration=duration
            )
            return False, None
            
        data = self.form_processor.getValidatedTodoData(field_map)
        return True, data
