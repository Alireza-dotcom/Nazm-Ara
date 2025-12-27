from pyqttoast import Toast, ToastPreset, ToastPosition
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont


class NotificationHandler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = self.window()


    def showToast(self, position, title, text, type, duration=3000):
        active_toast = Toast(self.parent_widget)
        active_toast.setTitleFont(QFont("Nunito", 15))
        active_toast.setTextFont(QFont("Nunito", 12))
        active_toast.applyPreset(self.notificationType(type))
        active_toast.setPosition(self.notificationPosition(position))
        active_toast.setDuration(duration)
        active_toast.setTitle(title)
        active_toast.setText(text)
        active_toast.show()

    def notificationType(self, type):
        if type == "success":
            return ToastPreset.SUCCESS
        elif type == "error":
            return ToastPreset.ERROR
        elif type == "info":
            return ToastPreset.INFORMATION
        elif type == "warning":
            return ToastPreset.WARNING
        else:
            return ToastPreset.INFORMATION


    def notificationPosition(self, position):
        if position == "top_right":
            return ToastPosition.TOP_RIGHT
        elif position == "top_left":
            return ToastPosition.TOP_LEFT
        elif position == "bottom_right":
            return ToastPosition.BOTTOM_RIGHT
        elif position == "bottom_left":
            return ToastPosition.BOTTOM_LEFT
        elif position == "top_middle":
            return ToastPosition.TOP_MIDDLE
        elif position == "bottom_middle":
            return ToastPosition.BOTTOM_MIDDLE
        elif position == "center":
            return ToastPosition.CENTER
        else:
            return ToastPosition.BOTTOM_RIGHT
