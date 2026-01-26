import pandas as pd
import pyqtgraph as pg
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

        upper = QHBoxLayout()
        habit_infos_layout = QVBoxLayout()
        total_days_frame = QFrame(parent=self)
        total_days_layout = QVBoxLayout(total_days_frame)
        total_days_layout.setContentsMargins(80, 20, 80, 20)
        total_days_text = QLabel(text="Total Days", parent=self)
        total_days = self.getTotalDays()
        self.total_days_digit = QLabel(text=f"{total_days} days", parent= self)
        total_days_layout.addWidget(total_days_text, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        total_days_layout.addWidget(self.total_days_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        current_streak_frame = QFrame(parent=self)
        current_streak_layout = QVBoxLayout(current_streak_frame)
        current_streak_layout.setContentsMargins(80, 20, 80, 20)
        current_streak_text = QLabel(text="Current streak", parent=self)
        current_streak = self.getCurrentStreak(self.daily_habits_date_list)
        self.current_streak_digit = QLabel(text=f"{current_streak} days", parent=self)
        current_streak_layout.addWidget(current_streak_text, alignment=Qt.AlignmentFlag.AlignCenter)
        current_streak_layout.addWidget(self.current_streak_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        best_streak_frame = QFrame(parent=self)
        best_streak_layout = QVBoxLayout(best_streak_frame)
        best_streak_layout.setContentsMargins(80, 20, 80, 20)
        best_streak_text = QLabel(text="Best streak", parent=self)
        best_streak = self.getBestStreak(self.daily_habits_date_list)
        self.best_streak_digit = QLabel(text=f"{best_streak} days", parent= self)
        best_streak_layout.addWidget(best_streak_text, alignment=Qt.AlignmentFlag.AlignCenter)
        best_streak_layout.addWidget(self.best_streak_digit, alignment=Qt.AlignmentFlag.AlignCenter)

        habit_infos_layout.addWidget(total_days_frame)
        habit_infos_layout.addWidget(current_streak_frame)
        habit_infos_layout.addWidget(best_streak_frame)

        self.calendar = HabitDetailsCalendar(habit_details=self.habit_details, daily_habits_map=self.daily_habits_map, parent=self)
        self.calendar.currentPageChanged.connect(self.calendarChanged)
        self.calendar.habit_doesnt_exist_signal.connect(self.createDailyHabitModal)
        self.calendar.habit_already_exist_signal.connect(self.editDailyHabitModal)
        upper.addWidget(self.calendar)
        upper.addLayout(habit_infos_layout)
        self.main_layout.addLayout(upper)

        #---- plot -------
        self.plot_widget = pg.PlotWidget()
        # non-interactive
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setBackground("black")
        # Ensure Y-axis starts at 0 and doesn't show negative space
        self.plot_widget.setLimits(yMin=0)
        self.main_layout.addWidget(self.plot_widget)

        self.updatePlot(self.current_day.year(), self.current_day.month())


    def calendarChanged(self, year: int, month: int):
        self.updatePlot(year, month) 


    def updatePlot(self, year: int, month: int):
        data_frame = pd.DataFrame.from_dict(self.daily_habits_map, orient='index')

        if data_frame.empty:
            self.plot_widget.clear()
            return

        data_frame = data_frame[["value"]] 
        data_frame.index = pd.to_datetime([data.toPython() for data in data_frame.index])
        data_frame["value"] = pd.to_numeric(data_frame["value"], errors="coerce")

        # This creates every day: 1, 2, 3, ... until the end of the month
        start_date = f"{year}-{month:02d}-01"
        days_in_month = pd.Period(start_date).days_in_month
        full_month_range = pd.date_range(start=start_date, periods=days_in_month)

        # It forces the DataFrame to have every day in the range. 
        # Missing days are filled with 0.
        final_df = data_frame.reindex(full_month_range, fill_value=0)

        # X will be the day numbers (1, 2, 3...)
        x_values = range(1, len(final_df) + 1)
        y_values = final_df["value"].values
        
        # Define Colors for each day
        colors = []
        for val in y_values:
            colors.append(self.getBarColor(val))

        self.plot_widget.clear()
        
        # Set X-axis ticks to show every few days or every day
        self.plot_widget.getAxis("bottom").setTicks([[(i, str(i)) for i in x_values]])
        
        bar_item = pg.BarGraphItem(
            x=x_values, 
            height=y_values, 
            width=0.7, 
            brushes=colors,
            pen="k"
        )
        
        self.plot_widget.addItem(bar_item)
        
        # Lock the view to the range of the month
        self.plot_widget.setXRange(0, len(x_values) + 1)
        self.plot_widget.setYRange(0, max(y_values) + 5 if len(y_values) > 0 and max(y_values) > 0 else 10)


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
            self.updateWidget()
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
            self.updateWidget()
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
            self.updateWidget()
        else:
            self.notification_handler.showToast(
                "bottom_right", "Couldn't Create Task",
                "A temporary error occurred. Please try again.", "error", duration=4000
            )


    def updateWidget(self):
        self.daily_habits_date_list = sorted(self.daily_habits_map)

        total_days = self.getTotalDays()
        self.total_days_digit.setText(f"{total_days} days")

        current_streak = self.getCurrentStreak(self.daily_habits_date_list)
        self.current_streak_digit.setText(f"{current_streak} days")

        best_streak = self.getBestStreak(self.daily_habits_date_list)
        self.best_streak_digit.setText(f"{best_streak} days")

        self.updatePlot(self.calendar.yearShown(), self.calendar.monthShown())


    def getBarColor(self, value: int):
        if value == 0:
            return "#dfe6e9" 

        color = self.habit_details.get("color")
        target = self.habit_details.get("target")
        if color == "blue":
            return "#0E34A7" if value >= target else "#3A4F7A"

        elif color == "red":
            return "#8B1E3F" if value >= target else "#8B354F"

        elif color == "green":
            return "#006633" if value >= target else "#4a8c6b" 

        elif color == "yellow":
            return "#FFCC00" if value >= target else "#e1c360" 

        elif color == "purple":
            return "#621b94" if value >= target else "#9d64c5" 

        elif color == "cyan":
            return "#009999" if value >= target else "#5ccbcb" 
