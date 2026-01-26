from modals import AddDailyHabitModalHabitDetailsWidget
from widgets import HabitDetailsCalendar, PushButton
from database_manager import DatabaseManager
from PySide6.QtGui import  QIcon
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)


class HabitDetailsWidget(QWidget):
    def __init__(self, habit_details: dict, daily_habits: list, parent: QWidget):
        super().__init__(parent=parent)

        self.habit_details = habit_details
        self.daily_habits_list = daily_habits
        self.database = DatabaseManager()
        self.current_day = QDate.currentDate()
        self.main_layout = QVBoxLayout(self)
        self.daily_habits_map = {}
        self.fillDateMap()
        self.daily_habits_date_list = sorted(self.daily_habits_map)

        self.back_btn = PushButton(parent=self)
        self.back_btn.setObjectName("BackButton")
        self.back_btn.setIcon(QIcon(":icons/previous_day.svg"))
        self.main_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        habit_infos_layout = QHBoxLayout()

        total_days_frame = QFrame(parent=self)
        total_days_layout = QVBoxLayout(total_days_frame)
        total_days_layout.setContentsMargins(40, 40 ,40 ,40)
        total_days_text = QLabel(text="Total Days", parent=self)
        total_days = self.getTotalDays()
        self.total_days_digit = QLabel(text=f"{total_days} days", parent= self)
        total_days_layout.addWidget(total_days_text, alignment=Qt.AlignmentFlag.AlignCenter)
        total_days_layout.addWidget(self.total_days_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        current_streak_frame = QFrame(parent=self)
        current_streak_layout = QVBoxLayout(current_streak_frame)
        current_streak_layout.setContentsMargins(40, 40 ,40 ,40)
        current_streak_text = QLabel(text="Current streak", parent=self)
        current_streak = self.getCurrentStreak(self.daily_habits_date_list)
        self.current_streak_digit = QLabel(text=f"{current_streak} days", parent=self)
        current_streak_layout.addWidget(current_streak_text, alignment=Qt.AlignmentFlag.AlignCenter)
        current_streak_layout.addWidget(self.current_streak_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        best_streak_frame = QFrame(parent=self)
        best_streak_layout = QVBoxLayout(best_streak_frame)
        best_streak_layout.setContentsMargins(40, 40 ,40 ,40)
        best_streak_text = QLabel(text="Best streak", parent=self)
        best_streak = self.getBestStreak(self.daily_habits_date_list)
        self.best_streak_digit = QLabel(text=f"{best_streak} days", parent= self)
        best_streak_layout.addWidget(best_streak_text, alignment=Qt.AlignmentFlag.AlignCenter)
        best_streak_layout.addWidget(self.best_streak_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        habit_infos_layout.addWidget(total_days_frame)
        habit_infos_layout.addWidget(current_streak_frame)
        habit_infos_layout.addWidget(best_streak_frame)
        self.main_layout.addLayout(habit_infos_layout)

        self.calendar = HabitDetailsCalendar(habit_details=self.habit_details, daily_habits_map=self.daily_habits_map, parent=self)
        self.calendar.habit_doesnt_exist_signal.connect(self.createDailyHabitModal)
        self.calendar.habit_already_exist_signal.connect(self.editDailyHabitModal)
        self.main_layout.addWidget(self.calendar)

        #TODO: add graph


    def fillDateMap(self):
        for rec in self.daily_habits_list:
            qdate = QDate.fromString(rec.get("date"), Qt.DateFormat.ISODate)
            self.daily_habits_map[qdate] = rec


    def getTotalDays(self):
        return len(self.daily_habits_map)


    def getCurrentStreak(self, dates: list):
        if not dates:
            return 0

        today = QDate.currentDate()

        streak = 0
        d = today

        while d in dates:
            streak += 1
            d = d.addDays(-1)

        return streak


    def getBestStreak(self, dates: list):
        if not dates:
            return 0

        best = 1
        current = 1

        for i in range(1, len(dates)):
            if dates[i - 1].addDays(1) == dates[i]:
                current += 1
                best = max(best, current)
            else:
                current = 1

        return best


    def createDailyHabitModal(self, date: QDate):
        self.modal = AddDailyHabitModalHabitDetailsWidget(self, date, self.habit_details)
        self.modal.add_daily_habit_clicked.connect(self.createDailyHabit)


    def editDailyHabitModal(self, date: QDate, daily_habits_detail: dict):
        self.modal = AddDailyHabitModalHabitDetailsWidget(self, date, self.habit_details, daily_habits_detail)
        self.modal.on_delete_clicked.connect(self.deleteDailyHabit)
        self.modal.on_update_clicked.connect(self.updateDailyHabit)


    def createDailyHabit(self, date: QDate, daily_habit_details: dict):
        """Adds a new daily habit to the database and update the button."""
        id = self.database.addDailyHabit(daily_habit_details.get("habit_id"),
                                         daily_habit_details.get("user_id"),
                                         daily_habit_details.get("date"),
                                         daily_habit_details.get("value")
                                        )
        details = self.database.getDailyHabitById(id)

        if id and details:
            self.calendar.colorDay(date=daily_habit_details.get("date"), value=daily_habit_details.get("value"))
            self.daily_habits_map.update({date: details})
            self.calendar.updateDailyHabitMap(self.daily_habits_map)
            self.updateHabitInfos()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def updateDailyHabit(self, date:QDate, daily_habit_details: dict):
        id = daily_habit_details.get("local_id")
        value = daily_habit_details.get("value")

        is_updated = self.database.updateDailyHabit(id, value)
        updated_details = self.database.getDailyHabitById(id)
        if is_updated and updated_details:
            self.calendar.colorDay(date=daily_habit_details.get("date"), value=daily_habit_details.get("value"))
            self.daily_habits_map.update({date: updated_details})
            self.calendar.updateDailyHabitMap(self.daily_habits_map)
            self.updateHabitInfos()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def deleteDailyHabit(self, date: QDate, id: int):
        if self.database.deleteDailyHabit(id):
            self.calendar.clearColorDay(date=date)
            self.daily_habits_map.pop(date)
            self.calendar.updateDailyHabitMap(self.daily_habits_map)
            self.updateHabitInfos()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def updateHabitInfos(self):
        self.daily_habits_date_list = sorted(self.daily_habits_map)

        total_days = self.getTotalDays()
        self.total_days_digit.setText(f"{total_days} days")

        current_streak = self.getCurrentStreak(self.daily_habits_date_list)
        self.current_streak_digit.setText(f"{current_streak} days")

        best_streak = self.getBestStreak(self.daily_habits_date_list)
        self.best_streak_digit.setText(f"{best_streak} days")
