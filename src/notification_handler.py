from pyqttoast import Toast, ToastPreset, ToastPosition
from PySide6.QtWidgets import QWidget


class NotificationHandler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


    def show_toast(self, position, title, text, type, duration=3000):
        toast = Toast(self)
        toast.applyPreset(self.notificationType(type))
        toast.setPosition(self.notificationPosition(position))
        toast.setDuration(duration)
        toast.setTitle(title)
        toast.setText(text)
        toast.show()


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
