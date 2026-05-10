from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QFileDialog
)
from PyQt6.QtCore import Qt

from settings_manager import (
    get_api_credentials, set_api_credentials,
    get_cookies_path, set_cookies_path,
)


class SettingsDialog(QDialog):
    """Dialog for configuring API credentials and cookies."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- API Credentials ---
        creds_group = QGroupBox("Telegram API Credentials")
        creds_layout = QFormLayout()
        creds_layout.setSpacing(10)

        self.txt_api_id = QLineEdit()
        self.txt_api_id.setPlaceholderText("Example: 20396198")
        creds_layout.addRow("API ID:", self.txt_api_id)

        self.txt_api_hash = QLineEdit()
        self.txt_api_hash.setPlaceholderText("Example: abcdef1234567890abcdef1234567890")
        self.txt_api_hash.setEchoMode(QLineEdit.EchoMode.Password)
        creds_layout.addRow("API HASH:", self.txt_api_hash)

        # Show/Hide password
        self.btn_toggle = QPushButton("Show")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.toggled.connect(self.toggle_password)
        creds_layout.addRow("", self.btn_toggle)

        creds_group.setLayout(creds_layout)
        layout.addWidget(creds_group)

        # --- Cookies ---
        cookies_group = QGroupBox("YouTube Cookies (optional)")
        cookies_layout = QHBoxLayout()

        self.lbl_cookies = QLabel("No file selected")
        self.lbl_cookies.setStyleSheet("color: gray;")
        self.lbl_cookies.setWordWrap(True)

        self.btn_browse_cookies = QPushButton("Browse...")
        self.btn_browse_cookies.clicked.connect(self.browse_cookies)

        self.btn_clear_cookies = QPushButton("Clear")
        self.btn_clear_cookies.clicked.connect(self.clear_cookies)

        cookies_layout.addWidget(self.lbl_cookies, stretch=1)
        cookies_layout.addWidget(self.btn_browse_cookies)
        cookies_layout.addWidget(self.btn_clear_cookies)
        cookies_group.setLayout(cookies_layout)
        layout.addWidget(cookies_group)

        # --- Info ---
        info_label = QLabel(
            "API ID and API HASH can be obtained at my.telegram.org\n\n"
            "Cookies (cookies.txt) help bypass age restrictions and anti-bot checks on YouTube.\n"
            "Get them using a browser extension like 'Get cookies.txt'."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)

        # --- Buttons ---
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.on_save)
        buttons_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)

        layout.addLayout(buttons_layout)

    def load_settings(self):
        """Loads current settings into the dialog."""
        creds = get_api_credentials()
        self.txt_api_id.setText(str(creds.get('api_id', '')))
        self.txt_api_hash.setText(creds.get('api_hash', ''))

        cookies_path = get_cookies_path()
        if cookies_path and cookies_path != '':
            self.lbl_cookies.setText(cookies_path)
            self.lbl_cookies.setStyleSheet("color: black;")
        else:
            self.lbl_cookies.setText("No file selected")
            self.lbl_cookies.setStyleSheet("color: gray;")

    def toggle_password(self, checked):
        """Shows/hides API HASH."""
        if checked:
            self.txt_api_hash.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle.setText("Hide")
        else:
            self.txt_api_hash.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle.setText("Show")

    def browse_cookies(self):
        """Opens file dialog to select cookies.txt."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select cookies.txt",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            self.lbl_cookies.setText(path)
            self.lbl_cookies.setStyleSheet("color: black;")

    def clear_cookies(self):
        """Clears the selected cookies file."""
        self.lbl_cookies.setText("No file selected")
        self.lbl_cookies.setStyleSheet("color: gray;")

    def on_save(self):
        """Saves all settings."""
        api_id = self.txt_api_id.text().strip()
        api_hash = self.txt_api_hash.text().strip()

        if not api_id or not api_hash:
            QMessageBox.warning(self, "Error", "API ID and API HASH are required.")
            return

        try:
            api_id = int(api_id)
        except ValueError:
            QMessageBox.warning(self, "Error", "API ID must be a number.")
            return

        set_api_credentials(api_id, api_hash)

        # Save cookies path
        cookies_text = self.lbl_cookies.text()
        if cookies_text != "No file selected":
            set_cookies_path(cookies_text)
        else:
            set_cookies_path("")

        QMessageBox.information(self, "Success", "Settings saved!")
        self.accept()
