from PySide6.QtCore import QFile, QTextStream


def loadStylesheet(app, resource_path):
    file = QFile(resource_path)

    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        file.close()
    else:
        print("Resource file doesn't exist")
        return
