import sys
import os
import asyncio
import hashlib

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QRadioButton, QCheckBox, QStatusBar, QButtonGroup,
    QMessageBox, QGroupBox, QMenuBar, QMenu, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from config_loader import get_config
from settings_manager import get_api_credentials
from settings_dialog import SettingsDialog
from caption_formatter import (
    format_caption_with_description,
    format_caption_without_description,
    add_tag_to_caption,
)
from youtube_downloader import (
    get_video_info,
    download_video,
    download_thumbnail,
    get_download_path,
    get_thumbnail_path,
    cleanup_files,
)
from telegram_client import TelegramClient


# ========== WORKER THREADS ==========

class ConnectWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, client: TelegramClient):
        super().__init__()
        self.client = client

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.client.connect())
            loop.close()

            if success:
                self.finished.emit(True, "[OK] Successfully connected to Telegram!")
            else:
                self.finished.emit(False, "[ERROR] Failed to connect to Telegram.")
        except Exception as e:
            self.finished.emit(False, f"[ERROR] Error: {str(e)}")


class GetInfoWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            info = get_video_info(self.url)
            self.finished.emit(info)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal(str, str)  # video_path, thumb_path
    error = pyqtSignal(str)

    def __init__(self, url: str, url_hash: str):
        super().__init__()
        self.url = url
        self.url_hash = url_hash
        self.video_path = get_download_path(url_hash)
        self.thumb_path = get_thumbnail_path(url_hash)

    def run(self):
        try:
            # Сначала получаем инфо для thumbnail
            info = get_video_info(self.url)
            thumbnail_url = info.get('thumbnail')

            # Скачиваем thumbnail
            if thumbnail_url:
                try:
                    thumb_result = asyncio.run(download_thumbnail(thumbnail_url, self.thumb_path))
                    if not thumb_result:
                        self.thumb_path = None
                except Exception:
                    self.thumb_path = None
            else:
                self.thumb_path = None

            # Скачиваем видео с прогрессом
            def progress_callback(data):
                self.progress.emit(data)

            download_video(self.url, self.video_path, progress_callback)

            self.finished.emit(self.video_path, self.thumb_path or "")

        except Exception as e:
            self.error.emit(str(e))


class SendWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, client: TelegramClient, video_path: str, caption: str, thumb_path: str = None,
                 duration: int = 0, width: int = 1920, height: int = 1080):
        super().__init__()
        self.client = client
        self.video_path = video_path
        self.caption = caption
        self.thumb_path = thumb_path
        self.duration = duration
        self.width = width
        self.height = height

    def run(self):
        try:
            success = asyncio.run(
                self.client.send_video(
                    self.video_path, self.caption, self.thumb_path,
                    duration=self.duration, width=self.width, height=self.height
                )
            )

            if success:
                self.finished.emit(True, "[OK] Video successfully sent to Saved Messages!")
            else:
                self.finished.emit(False, "[ERROR] Failed to send video.")

        except Exception as e:
            self.finished.emit(False, f"[ERROR] Error: {str(e)}")


# ========== MAIN WINDOW ==========

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to Telegram Desktop")
        self.setMinimumSize(700, 650)

        # Данные
        self.current_url = ""
        self.current_info = None
        self.url_hash = ""
        self.video_path = ""
        self.thumb_path = ""
        self.video_meta = {}  # width, height, duration
        self.base_caption_with_desc = ""
        self.base_caption_without_desc = ""
        self.current_caption = ""
        self.use_description = True
        self.tags = []

        # Telegram клиент (создается позже)
        self.tg_client = None

        self.init_menu()
        self.init_ui()
        self.check_credentials()

    def init_menu(self):
        """Создает меню приложения."""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        settings_action = file_menu.addAction("Настройки...")
        settings_action.triggered.connect(self.open_settings)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

    def open_settings(self):
        """Открывает окно настроек."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Пересоздаем клиент с новыми credentials
            self.check_credentials()

    def check_credentials(self):
        """Проверяет наличие API credentials и создает клиент."""
        creds = get_api_credentials()
        api_id = creds.get('api_id')
        api_hash = creds.get('api_hash')

        if not api_id or not api_hash:
            QMessageBox.warning(
                self,
                "Настройки не заданы",
                "API ID и API HASH не настроены.\n\n"
                "Откройте Файл -> Настройки и введите свои данные с my.telegram.org"
            )
            return

        try:
            config = get_config()
            self.tg_client = TelegramClient(config['api_id'], config['api_hash'])
            self.status_bar.showMessage("Ready. Click 'Connect' to login to Telegram.")
        except ValueError as e:
            QMessageBox.warning(self, "Configuration Error", str(e))

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Telegram Connection ---
        tg_group = QGroupBox("Telegram")
        tg_layout = QHBoxLayout()
        self.lbl_tg_status = QLabel("[OFFLINE] Not connected")
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        tg_layout.addWidget(self.lbl_tg_status)
        tg_layout.addStretch()
        tg_layout.addWidget(self.btn_connect)
        tg_group.setLayout(tg_layout)
        layout.addWidget(tg_group)

        # --- URL Input ---
        url_group = QGroupBox("YouTube URL")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.btn_get_info = QPushButton("Get Info")
        self.btn_get_info.clicked.connect(self.on_get_info_clicked)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.btn_get_info)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # --- Video Info ---
        info_group = QGroupBox("Video Info")
        info_layout = QVBoxLayout()
        self.lbl_title = QLabel("Title: -")
        self.lbl_uploader = QLabel("Channel: -")
        self.lbl_duration = QLabel("Duration: -")
        info_layout.addWidget(self.lbl_title)
        info_layout.addWidget(self.lbl_uploader)
        info_layout.addWidget(self.lbl_duration)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # --- Caption Type ---
        caption_type_group = QGroupBox("Caption Format")
        caption_type_layout = QHBoxLayout()
        self.radio_with_desc = QRadioButton("With description")
        self.radio_without_desc = QRadioButton("Without description")
        self.radio_with_desc.setChecked(True)
        self.radio_with_desc.toggled.connect(self.on_caption_type_changed)
        self.radio_without_desc.toggled.connect(self.on_caption_type_changed)
        caption_type_layout.addWidget(self.radio_with_desc)
        caption_type_layout.addWidget(self.radio_without_desc)
        caption_type_layout.addStretch()
        caption_type_group.setLayout(caption_type_layout)
        layout.addWidget(caption_type_group)

        # --- Tags ---
        tags_group = QGroupBox("Tag (select one)")
        tags_layout = QHBoxLayout()
        self.chk_gp = QCheckBox("#gp")
        self.chk_deco = QCheckBox("#deco")
        self.chk_gp_deco = QCheckBox("#gp_deco")
        self.chk_preview = QCheckBox("#preview")
        
        # Группа: только 1 тег за раз
        self.tag_group = QButtonGroup()
        self.tag_group.setExclusive(True)
        self.tag_group.addButton(self.chk_gp)
        self.tag_group.addButton(self.chk_deco)
        self.tag_group.addButton(self.chk_gp_deco)
        self.tag_group.addButton(self.chk_preview)
        self.tag_group.idToggled.connect(self.on_tag_changed)
        
        tags_layout.addWidget(self.chk_gp)
        tags_layout.addWidget(self.chk_deco)
        tags_layout.addWidget(self.chk_gp_deco)
        tags_layout.addWidget(self.chk_preview)
        tags_layout.addStretch()
        tags_group.setLayout(tags_layout)
        layout.addWidget(tags_group)

        # --- Caption Editor ---
        caption_group = QGroupBox("Caption (editable)")
        caption_layout = QVBoxLayout()
        self.caption_edit = QTextEdit()
        self.caption_edit.setPlaceholderText("Caption will appear here after getting video info...")
        caption_layout.addWidget(self.caption_edit)
        caption_group.setLayout(caption_layout)
        layout.addWidget(caption_group)

        # --- Progress ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        layout.addWidget(self.progress_bar)

        # --- Buttons ---
        buttons_layout = QHBoxLayout()
        self.btn_download = QPushButton("[ DOWNLOAD ]")
        self.btn_download.setEnabled(False)
        self.btn_download.clicked.connect(self.on_download_clicked)

        self.btn_send = QPushButton("[ SEND TO TELEGRAM ]")
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self.on_send_clicked)

        buttons_layout.addWidget(self.btn_download)
        buttons_layout.addWidget(self.btn_send)
        layout.addLayout(buttons_layout)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Open File -> Settings to configure API credentials.")

    def on_connect_clicked(self):
        if not self.tg_client:
            QMessageBox.warning(self, "Error", "Please configure API credentials in Settings first.")
            self.open_settings()
            return

        self.btn_connect.setEnabled(False)
        self.lbl_tg_status.setText("[CONNECTING] ...")
        self.status_bar.showMessage("Connecting to Telegram... Follow instructions in console.")

        self.worker_connect = ConnectWorker(self.tg_client)
        self.worker_connect.finished.connect(self.on_connect_finished)
        self.worker_connect.start()

    def on_connect_finished(self, success: bool, message: str):
        if success:
            self.lbl_tg_status.setText("[ONLINE] Connected")
            self.btn_connect.setEnabled(False)
            self.status_bar.showMessage("[OK] Connected to Telegram. Ready to get video info.")
        else:
            self.lbl_tg_status.setText("[ERROR] Connection failed")
            self.btn_connect.setEnabled(True)
            self.status_bar.showMessage("[ERROR] Connection failed")
            QMessageBox.critical(self, "Error", message)

    def on_get_info_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Enter a YouTube video URL.")
            return

        self.current_url = url
        self.url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Сбрасываем все теги при новом видео
        self.tag_group.setExclusive(False)
        self.chk_gp.setChecked(False)
        self.chk_deco.setChecked(False)
        self.chk_gp_deco.setChecked(False)
        self.chk_preview.setChecked(False)
        self.tag_group.setExclusive(True)

        self.btn_get_info.setEnabled(False)
        self.status_bar.showMessage("Getting video info...")

        self.worker_info = GetInfoWorker(url)
        self.worker_info.finished.connect(self.on_info_received)
        self.worker_info.error.connect(self.on_info_error)
        self.worker_info.start()

    def on_info_received(self, info: dict):
        self.current_info = info

        self.lbl_title.setText(f"Title: {info['title']}")
        self.lbl_uploader.setText(f"Channel: {info['uploader']}")
        duration = info.get('duration', 0)
        if duration:
            mins = duration // 60
            secs = duration % 60
            self.lbl_duration.setText(f"Duration: {mins}:{secs:02d}")
        else:
            self.lbl_duration.setText("Duration: -")

        # Сохраняем метаданные для отправки
        self.video_meta = {
            'duration': int(info.get('duration', 0)),
            'width': int(info.get('width', 1920)),
            'height': int(info.get('height', 1080)),
        }

        # Генерируем базовые caption
        self.base_caption_with_desc = format_caption_with_description(
            info['title'], info['uploader'], info['url'], info['description']
        )
        self.base_caption_without_desc = format_caption_without_description(
            info['title'], info['uploader'], info['url']
        )

        # Применяем текущие теги
        self.update_caption_display()

        self.btn_download.setEnabled(True)
        self.btn_get_info.setEnabled(True)
        self.status_bar.showMessage("[OK] Info received. Ready to download.")

    def on_info_error(self, error_msg: str):
        QMessageBox.critical(self, "Error", f"Failed to get info:\n{error_msg}")
        self.btn_get_info.setEnabled(True)
        self.status_bar.showMessage("[ERROR] Failed to get info")

    def on_caption_type_changed(self):
        self.use_description = self.radio_with_desc.isChecked()
        self.update_caption_display()

    def on_tag_changed(self, id=None, checked=None):
        self.update_caption_display()

    def update_caption_display(self):
        """Обновляет текст в caption_edit на основе выбранных опций."""
        if not self.current_info:
            return

        # Базовый caption
        if self.use_description:
            caption = self.base_caption_with_desc
        else:
            caption = self.base_caption_without_desc

        # Добавляем теги
        tags = []
        if self.chk_gp.isChecked():
            tags.append("gp")
        if self.chk_deco.isChecked():
            tags.append("deco")
        if self.chk_gp_deco.isChecked():
            tags.append("gp_deco")
        if self.chk_preview.isChecked():
            tags.append("preview")

        for tag in tags:
            caption = add_tag_to_caption(caption, tag)

        self.current_caption = caption
        self.caption_edit.setPlainText(caption)

    def on_download_clicked(self):
        if not self.current_url:
            return

        self.btn_download.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Downloading... %p%")
        self.status_bar.showMessage("Downloading video...")

        # Очищаем старые файлы
        cleanup_files(self.url_hash)

        self.worker_download = DownloadWorker(self.current_url, self.url_hash)
        self.worker_download.progress.connect(self.on_download_progress)
        self.worker_download.finished.connect(self.on_download_finished)
        self.worker_download.error.connect(self.on_download_error)
        self.worker_download.start()

    def on_download_progress(self, data: dict):
        if data['status'] == 'downloading':
            percent = data.get('percent', 0)
            self.progress_bar.setValue(int(percent))
            speed = data.get('speed', 0)
            if speed:
                speed_mb = speed / 1024 / 1024
                self.progress_bar.setFormat(f"Downloading... %p% ({speed_mb:.1f} MB/s)")
        elif data['status'] == 'finished':
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Download complete!")

    def on_download_finished(self, video_path: str, thumb_path: str):
        self.video_path = video_path
        self.thumb_path = thumb_path if thumb_path else None

        self.btn_download.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.status_bar.showMessage(f"[OK] Video downloaded: {os.path.basename(video_path)}")
        QMessageBox.information(self, "Done", "Video downloaded! Now you can send to Telegram.")

    def on_download_error(self, error_msg: str):
        self.btn_download.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Download error")
        QMessageBox.critical(self, "Error", f"Failed to download video:\n{error_msg}")
        self.status_bar.showMessage("[ERROR] Download failed")

    def on_send_clicked(self):
        if not self.video_path or not os.path.exists(self.video_path):
            QMessageBox.warning(self, "Error", "Download a video first.")
            return

        # Если не подключены - сначала подключаемся
        if not self.tg_client or not self.tg_client.is_connected():
            reply = QMessageBox.question(
                self,
                "Not connected",
                "Telegram is not connected. Connect now?\n\n"
                "(You will need to enter phone number and code in console)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.on_connect_clicked()
            return

        self.btn_send.setEnabled(False)
        self.status_bar.showMessage("Sending to Telegram...")

        caption = self.caption_edit.toPlainText()

        self.worker_send = SendWorker(
            self.tg_client, self.video_path, caption, self.thumb_path,
            duration=self.video_meta.get('duration', 0),
            width=self.video_meta.get('width', 1920),
            height=self.video_meta.get('height', 1080)
        )
        self.worker_send.finished.connect(self.on_send_finished)
        self.worker_send.start()

    def on_send_finished(self, success: bool, message: str):
        self.btn_send.setEnabled(True)
        if success:
            self.status_bar.showMessage("[OK] Video sent to Saved Messages!")
            QMessageBox.information(self, "Success", message)
            # Удаляем локальные файлы после успешной отправки
            cleanup_files(self.url_hash)
            self.video_path = ""
            self.thumb_path = ""
            self.status_bar.showMessage("[OK] Done. Files cleaned.")
        else:
            self.status_bar.showMessage("[ERROR] Send failed")
            QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        """При закрытии окна отключаемся от Telegram и чистим файлы."""
        try:
            if self.tg_client:
                self.tg_client.disconnect()
        except:
            pass
        # Чистим оставшиеся файлы
        if self.url_hash:
            cleanup_files(self.url_hash)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
