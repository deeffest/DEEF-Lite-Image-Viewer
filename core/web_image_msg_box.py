#web_image_msg_box.py
from PyQt5.QtCore import QUrl, QByteArray
from PyQt5.QtGui import QImageReader
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit, PushButton
    )
import os

class WebImageMsgBox(MessageBoxBase):
    def __init__(self, app_settings, current_last_opened_folder, tr, current_image_path=None, parent=None):
        super().__init__(parent)
        self.current_image_path = current_image_path
        self.app_settings = app_settings
        self.parent = parent
        self.tr = tr

        self.titleLabel = SubtitleLabel(self.tr["35"], self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText(
            "https://example.com/image.png")
        self.urlLineEdit.setClearButtonEnabled(True)
        self.urlLineEdit.setText(self.current_image_path)
        self.urlLineEdit.selectAll()

        self.browsePushButton = PushButton(self.tr["36"])
        self.browsePushButton.clicked.connect(self.browse_files)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addWidget(self.browsePushButton)

        self.yesButton.setText(self.tr["1"])
        self.cancelButton.setText(self.tr["37"])

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)
        self.urlLineEdit.textChanged.connect(self._validateUrl)
        self.urlLineEdit.setFocus()

    def _validateUrl(self, text):
        if os.path.isfile(text):  
            is_image = QImageReader(text).format() is not None
            self.yesButton.setEnabled(is_image)
        else:
            url = QUrl(text)
            if url.isValid() and (url.scheme() in ["http", "https"] or url.isLocalFile()):
                if url.scheme() in ["http", "https"]:
                    networkManager = QNetworkAccessManager(self)
                    networkManager.finished.connect(self.handleNetworkData)
                    networkManager.head(QNetworkRequest(url))
                elif url.isLocalFile(): 
                    local_file_path = url.toLocalFile()
                    is_image = QImageReader(local_file_path).format() is not None
                    self.yesButton.setEnabled(is_image)
            else:
                self.yesButton.setDisabled(True)

    def handleNetworkData(self, networkReply):
        header = networkReply.header(QNetworkRequest.ContentTypeHeader)
        is_image_url = "image" in header if header else False
        self.yesButton.setEnabled(is_image_url)

    def browse_files(self):
        image_formats = ["*." + QByteArray(ext).data().decode() for ext in QImageReader.supportedImageFormats()]
        image_filter = "Images (" + " ".join(image_formats) + ")"

        file_dlg = QFileDialog(self)
        file_dlg.setDirectory(self.parent.current_last_opened_folder)
        file_path, _ = file_dlg.getOpenFileName(
            self, self.tr["1"], "", image_filter
        )

        if file_path:
            self.parent.current_last_opened_folder = os.path.dirname(file_path)
            self.app_settings.setValue(
                "current_last_opened_folder", 
                self.parent.current_last_opened_folder
            )

            self.urlLineEdit.clear()
            self.urlLineEdit.setText(file_path)