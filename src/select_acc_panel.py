from PySide6.QtCore import Qt, Signal, QMargins
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QWidget
)
from widgets import ClickableLabel, AccountListItemWidget, ScalableSvgWidget
from database_manager import DatabaseManager


class SelectAccountPanel(QFrame):
    """Panel that displays a list of existing user accounts for selection."""
    account_selected = Signal(dict)
    add_account_clicked = Signal()

    SPACING_SIZE = 40
    CONTENTS_MARGINS_SIZE = QMargins(50, 40, 50, 40)

    def __init__(self, parent: QWidget, accounts_detail_list: list):
        super().__init__(parent)
        self.setObjectName("SelectAccountPanel")
        self.database = DatabaseManager()
        self.accounts_detail_list = accounts_detail_list

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SelectAccountPanel.CONTENTS_MARGINS_SIZE)
        layout.setSpacing(SelectAccountPanel.SPACING_SIZE)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = ScalableSvgWidget(svg_path=":logos/logo.svg", parent=self)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel(text="Select an Account", parent=self)
        title.setObjectName("TitleLabel")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.list_widget = QListWidget(parent=self)
        self.list_widget.horizontalScrollBar()
        self.list_widget.setMinimumSize(200, 282)
        # Disable default focus and selection highlights for a cleaner UI
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_widget.itemDoubleClicked.connect(self.onAccountDoubleClicked)
            
        layout.addWidget(self.list_widget)

        add_account_label = ClickableLabel(text="Add another Account", parent=self)
        add_account_label.clicked.connect(lambda: self.add_account_clicked.emit())
        layout.addWidget(add_account_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loadAccounts()


    def loadAccounts(self):
        """populates the QListWidget with custom widgets."""
        for acc_details in self.accounts_detail_list:
            # Create a container item for the QListWidget
            item = QListWidgetItem(self.list_widget)
            # Store the raw account data within the item for easy retrieval
            item.setData(Qt.ItemDataRole.UserRole, acc_details)
            # Use custom widget for displaying account details
            custom_widget = AccountListItemWidget(widget_item=item, parent=self.list_widget)
            # Ensure the list item matches the custom widget's size requirements
            item.setSizeHint(custom_widget.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)


    def onAccountDoubleClicked(self, item: QListWidgetItem):
        """Extracts stored user data and notifies the parent window to log into account."""
        account_details = item.data(Qt.ItemDataRole.UserRole)
        self.account_selected.emit(account_details)
