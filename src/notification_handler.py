from pyqttoast import Toast, ToastPreset, ToastPosition
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont


class NotificationHandler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


    def showToast(self, position, title, text, type, duration=3000, source_widget=None):
        self.active_toast = Toast(self)
        self.active_toast.setTitleFont(QFont("Nunito", 15))
        self.active_toast.setTextFont(QFont("Nunito", 12))
        self.active_toast.applyPreset(self.notificationType(type))
        self.active_toast.setPosition(self.notificationPosition(position))
        self.active_toast.setDuration(duration)
        self.active_toast.setTitle(title)
        self.active_toast.setText(text)
        self.disableWidget(source_widget)
        self.active_toast.closed.connect(lambda: self.enableWidget(source_widget) if source_widget else None)
        self.active_toast.show()


    def enableWidget(self, widget):
        if widget:
            widget.setEnabled(True)


    def disableWidget(self, widget):
        if widget:
            widget.setEnabled(False)


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
