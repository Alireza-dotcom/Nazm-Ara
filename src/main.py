import sys
from login_panel import LoginPanel

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QMainWindow,
    QHBoxLayout,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")

        self.setMinimumSize(1024, 768)
        self.resize(1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()

        self.showLoginPage()

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.stack)


    def showLoginPage(self):
        self.login_panel = self.loadPage(LoginPanel)


    def loadPage(self, ClassWidget):
        previous_widget = self.stack.currentWidget()

        new_widget = ClassWidget(self)
        index = self.stack.addWidget(new_widget)

        self.stack.setCurrentIndex(index)
        if previous_widget:
            self.stack.removeWidget(previous_widget)
            previous_widget.deleteLater()
        
        return new_widget


    def resizeEvent(self, event):
        MIN_PANEL_WIDTH = 430
        PANEL_WIDTH_RATIO = 0.32

        window_width = self.width()
        target_width = max(MIN_PANEL_WIDTH, int(window_width * PANEL_WIDTH_RATIO)) # 32% of width, min 430px
        self.stack.setFixedWidth(target_width)

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Nazm Ara")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
