from PySide6.QtCore import Qt, Signal, QMargins
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtGui import QPixmap

from widgets import ClickableLabel, AccountListItemWidget
from database_manager import DatabaseManager


class SelectAccountPanel(QFrame):
    account_selected = Signal(dict)
    add_account_clicked = Signal()

    SPACING_SIZE = 40
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SelectAccountPanel")

        self.database = DatabaseManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SelectAccountPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SelectAccountPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignTop)

        # Logo
        logo = QLabel(self)
        logo_file = QPixmap(":logos/logo.svg")
        logo.setPixmap(logo_file)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)

        # Title
        title = QLabel("Select an Account", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Accounts list
        self.list_widget = QListWidget(self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setMinimumSize(200, 282)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_widget.itemDoubleClicked.connect(self.onAccountDoubleClicked)
        layout.addWidget(self.list_widget)

        # Add account link
        add_account_label = ClickableLabel("Add another Account", self)
        add_account_label.setAlignment(Qt.AlignCenter)
        add_account_label.clicked.connect(self.onAddAccountClicked)
        layout.addWidget(add_account_label)

        self.loadAccounts()


    def loadAccounts(self):
        accounts = self.database.getListOfUsers()

        for row in accounts:
            item = QListWidgetItem(self.list_widget)
            custom_widget = AccountListItemWidget(row, self)
            item.setSizeHint(custom_widget.sizeHint())
            item.setData(Qt.UserRole, row)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def onAccountDoubleClicked(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if isinstance(data, dict):
            self.account_selected.emit(data)

    def onAddAccountClicked(self):
        self.add_account_clicked.emit()
