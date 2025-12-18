from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QFontDatabase, QFontMetrics


def loadStylesheet(app, resource_path):
    file = QFile(resource_path)

    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        file.close()
    else:
        print("Resource file doesn't exist")
        return


def loadFont(font_path):
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id < 0:
        print(f"Failed to load font: {font_path}")

    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if not font_families:
        print(f"No font families found in: {font_path}")

    return font_families[0]
