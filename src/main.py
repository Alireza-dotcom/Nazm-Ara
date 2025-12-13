import sys

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

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.stack)


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Nazm Ara")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
