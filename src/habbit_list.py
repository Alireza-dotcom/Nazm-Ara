from widgets import PushButton, HabitListItemWidget, HabitButton
from modals import AddHabitModal, AddDailyHabitModal
from notification_handler import NotificationHandler
from database_manager import DatabaseManager

from PySide6.QtCore import (
    Qt,
    QDate
)
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem
)

class HabitWidget(QWidget):
    """habit management view."""
    STRETCH_SIZE = 1

    def __init__(self, parent: QWidget, account_details: dict):
        super().__init__(parent)
        self.account_details = account_details
        self.database = DatabaseManager()
        self.notification_handler = NotificationHandler()
        self.currrent_date = QDate.currentDate()
        self.main_layout = QVBoxLayout(self)

        # Calendar & Date Controls Header
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("AddHabitFrame")

        self.header_layout = QVBoxLayout(self.header_frame)
        self.header_layout.setSpacing(10)
        self.add_habit_layout = QHBoxLayout()
        self.add_habit_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.add_habit_btn = PushButton("+ Add habit", self)
        self.add_habit_btn.setObjectName("AddHabitBtn")
        self.add_habit_btn.clicked.connect(self.showHabitCreateModal)

        self.add_habit_layout.addStretch(HabitWidget.STRETCH_SIZE)
        self.add_habit_layout.addWidget(self.add_habit_btn)
        self.header_layout.addLayout(self.add_habit_layout)

        self.labels_layout = QHBoxLayout()
        label = QLabel("Habit", self)
        label.setObjectName("HabitLabel")
        self.labels_layout.addWidget(label)
        self.addHeaderLabels()

        self.header_layout.addLayout(self.labels_layout)
        self.main_layout.addWidget(self.header_frame)

        # Task List Display
        self.list_widget = QListWidget(self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.main_layout.addWidget(self.list_widget)

        # Initial data load
        self.loadHabits()


    def resetStyleSheet(self):
        self.window().style_sheet_handler.updateStylesheet()


    def addHeaderLabels(self):
        for i in range(-4, 1, 1):
            label = QLabel(self.currrent_date.addDays(i).toString("ddd\nd"), self)
            label.setObjectName("DateLabel")
            label.setFixedWidth(90)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.labels_layout.addWidget(label)

    # ==================== HABITS ====================

    def loadHabits(self):
        """Retrieves habits from the database and renders them."""
        habits = self.database.getAllHabits(self.account_details.get("id"))

        for row in habits:
            item = QListWidgetItem(self.list_widget)
            custom_widget = HabitListItemWidget(row, self)
            self.loadHabitButtons(row, custom_widget) 
            self.connectHabitButtonsSignals(custom_widget)
            custom_widget.on_edit_button_clicked.connect(self.showHabitEditModal)

            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def loadHabitButtons(self, row: dict, widget: HabitListItemWidget):
        habit_id = row.get("local_id")
        user_id = self.account_details.get("id")
        start_date = self.currrent_date.addDays(-4).toString(Qt.ISODate)
        end_date = self.currrent_date.toString(Qt.ISODate)
        daily_habits = self.database.getDailyHabitRange(habit_id, user_id, start_date, end_date)

        # convert dates to iso format so i can compare them with data that i fetched from db
        buttons_date_in_iso_format = []
        for btn in widget.button_list:
            iso_format = btn.date.toString(Qt.DateFormat.ISODate) 
            buttons_date_in_iso_format.append(iso_format)

        for daily_habit_details in daily_habits:
            index = buttons_date_in_iso_format.index(daily_habit_details["date"])
            btn_widget = widget.button_list[index]
            btn_widget.daily_habit_details = daily_habit_details
            value = int(daily_habit_details.get("value"))
            target = int(daily_habit_details.get("target"))
            color = daily_habit_details.get("color")
            self.applyStyleToDailyHabits(btn_widget, value, target, color)


    def connectHabitButtonsSignals(self, widget: HabitListItemWidget):
        for button in widget.button_list:
            button.on_habit_button_clicked.connect(self.showDailyHabitModal)


    def showHabitCreateModal(self):
        """Opens the modal to create a new habit."""
        self.modal = AddHabitModal(self, False)
        self.modal.add_habit_clicked.connect(self.createHabit)


    def createHabit(self, details: list):
        """Adds a new habit to the database and add it into the current view."""
        user_id = self.account_details.get("id")
        habit_id = self.database.addHabit(user_id, details.get("title"),details.get("question"),
                                          details.get("unit"), details.get("target"),
                                          details.get("color"), details.get("description"))
        if habit_id:
            details["local_id"] = habit_id
            details["user_id"] = self.account_details["id"]

            item = QListWidgetItem(self.list_widget)
            custom_widget = HabitListItemWidget(details, self)
            custom_widget.on_edit_button_clicked.connect(self.showHabitEditModal)
            self.connectHabitButtonsSignals(custom_widget)
            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def showHabitEditModal(self, habit_object: HabitListItemWidget, habit_details: dict):
        """Opens the modal to edit or delete an existing habit."""
        self.modal = AddHabitModal(self, habit_object, habit_details)
        self.modal.on_update_clicked.connect(self.updateHabit)
        self.modal.on_delete_clicked.connect(self.deleteHabit)


    def updateHabit(self, habit_object: HabitListItemWidget, data: dict, local_id: str):
        """Validates and saves modifications to an existing task."""
        title = data.get("title")
        description = data.get("description")
        priority = data.get("priority")
        color = data.get("color")
        question = data.get("question")
        target = data.get("target")
        unit = data.get("unit")
        if self.database.updateHabit(local_id, title=title, description=description,
                                     priority=priority, color=color,
                                     question=question, target=target, unit=unit):
            habit_object.update(data)

            for button in habit_object.button_list:
                btn_details = button.daily_habit_details
                if btn_details:
                    btn_details.update({"target": data.get("target")})
                    self.applyStyleToDailyHabits(button, btn_details.get("value"),
                                                btn_details.get("target"), color)

            # Refresh stylesheet to apply priority-based color change
            self.resetStyleSheet()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def deleteHabit(self, habit_object: HabitListItemWidget, local_id: str):
        """Removes a habit from the database and the UI list."""
        if self.database.deleteHabit(local_id):
            item = self.list_widget.itemAt(habit_object.pos())
            row = self.list_widget.row(item)
            taken_item = self.list_widget.takeItem(row) # Removes the item from view
            del taken_item
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )

    # ==================== DAILY HABITS ====================

    def showDailyHabitModal(self, habit_button_object: HabitButton, date: QDate, habit_details: dict, daily_habit_details: dict):
        print(daily_habit_details)
        self.modal = AddDailyHabitModal(self, date, habit_button_object, habit_details, daily_habit_details)
        if not daily_habit_details:
            self.modal.add_daily_habit_clicked.connect(self.createDailyHabit)
        else:
            self.modal.on_delete_clicked.connect(self.deleteDailyHabit)
            self.modal.on_update_clicked.connect(self.updateDailyHabit)


    def updateDailyHabit(self, item_object: QWidget, data: dict):
        id = data.get("local_id")
        target = data.get("target")
        color = data.get("color")
        value = data.get("value")

        is_updated = self.database.updateDailyHabit(id, value)
        updated_details = self.database.getDailyHabitById(id)
        if is_updated and updated_details:
            item_object.daily_habit_details = updated_details
            self.applyStyleToDailyHabits(item_object, value, target, color)

            # Refresh stylesheet to apply priority-based color change
            self.resetStyleSheet()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def deleteDailyHabit(self, button_widget: QWidget, id: int):
        if self.database.deleteDailyHabit(id):
            button_widget.setObjName("HabitButton")
            button_widget.daily_habit_details = {}

            # Refresh stylesheet to apply priority-based color change
            self.resetStyleSheet()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def createDailyHabit(self, button_widget: QWidget, data: dict):
        """Adds a new daily habit to the database and update the button."""
        id = self.database.addDailyHabit(data.get("habit_id"), data.get("user_id"),
                                          data.get("date"), data.get("value"))
        details = self.database.getDailyHabitById(id)

        if id and details:
            self.applyStyleToDailyHabits(button_widget, data.get("value"),
                                         data.get("target"), data.get("color"))
            button_widget.daily_habit_details = details
            # Refresh stylesheet to apply priority-based color change
            self.resetStyleSheet()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def applyStyleToDailyHabits(self, button_obj: QWidget, value: int, target: int, color: str):
        object_name = f"{color.title()}Color" if value >= target else f"Lesser{color.title()}Color"
        button_obj.setObjectName(object_name)
