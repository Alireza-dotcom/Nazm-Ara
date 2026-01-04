from pyqttoast import Toast, ToastPreset, ToastPosition
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QColor


class NotificationHandler(QWidget):
    """Manages the creation and styling of toast notifications using the pyqttoast library."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Identify the top-level window to ensure toasts overlay the entire application
        self.parent_widget = self.window()


    def showToast(self, position: str, title: str, text: str, type: str, duration: int = 3000):
        """ Creates, styles, and displays a toast notification with the specified parameters. """
        active_toast = Toast(self.parent_widget)
        active_toast.applyPreset(self.notificationType(type))
        active_toast.setPosition(self.notificationPosition(position))
        active_toast.setDuration(duration)
        active_toast.setTitle(title)
        active_toast.setText(text)
        self.setStyle(active_toast)
        active_toast.show()


    def notificationType(self, type: str):
        """ Maps a string identifier to a ToastPreset Enum. """
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


    def notificationPosition(self, position: str):
        """ Maps a string identifier to a ToastPosition Enum. """
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


    def setStyle(self, toast: Toast):
        """ Customizes the visual appearance of the toast to match the app theme. """
        toast.setBorderRadius(5)
        toast.setBackgroundColor(QColor("#323339"))
        toast.setTitleColor(QColor("#ffffff"))
        toast.setTextColor(QColor("#ffffff"))
        toast.setCloseButtonIconColor(QColor("#ffffff"))

        # Apply Nunito font to maintain consistency with Latin text styling
        toast.setTitleFont(QFont("Nunito", 15))
        toast.setTextFont(QFont("Nunito", 12))
