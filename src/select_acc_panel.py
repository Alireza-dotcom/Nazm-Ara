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
    """Panel that displays a list of existing user accounts for selection."""
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

        logo = QLabel(self)
        logo.setPixmap(QPixmap(":logos/logo.svg"))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo, alignment=Qt.AlignCenter)

        title = QLabel("Select an Account", self)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.list_widget = QListWidget(self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setMinimumSize(200, 282)
        # Disable default focus and selection highlights for a cleaner UI
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_widget.itemDoubleClicked.connect(self.onAccountDoubleClicked)
        layout.addWidget(self.list_widget)

        add_account_label = ClickableLabel("Add another Account", self)
        add_account_label.setAlignment(Qt.AlignCenter)
        add_account_label.clicked.connect(lambda: self.add_account_clicked.emit())
        layout.addWidget(add_account_label)

        self.loadAccounts()


    def loadAccounts(self):
        """Fetches users from the database and populates the QListWidget with custom widgets."""
        accounts = self.database.getListOfUsers()

        for row in accounts:
            # Create a container item for the QListWidget
            item = QListWidgetItem(self.list_widget)
            # Use custom widget for displaying account details
            custom_widget = AccountListItemWidget(row, self)
            # Ensure the list item matches the custom widget's size requirements
            item.setSizeHint(custom_widget.sizeHint())
            # Store the raw account data within the item for easy retrieval
            item.setData(Qt.UserRole, row)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def onAccountDoubleClicked(self, item: QListWidgetItem):
        """Extracts stored user data and notifies the parent window to log into account."""
        data = item.data(Qt.UserRole)
        if isinstance(data, dict):
            self.account_selected.emit(data)
