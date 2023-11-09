#web_image_msg_box.py
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit 
    )

class WebImageMsgBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("Enter the URL of the image", self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText(
            "https://example.com/image.png")
        self.urlLineEdit.setClearButtonEnabled(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        self.yesButton.setText("Open image")
        self.cancelButton.setText("Cancel")

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)
        self.urlLineEdit.textChanged.connect(self._validateUrl)
        self.urlLineEdit.setFocus()

    def _validateUrl(self, text):
        url = QUrl(text)
        if url.isValid() and url.scheme() in ["http", "https"]:
            networkManager = QNetworkAccessManager(self)
            networkManager.finished.connect(self.handleNetworkData)
            networkManager.head(QNetworkRequest(QUrl(url)))

    def handleNetworkData(self, networkReply):
        header = networkReply.header(QNetworkRequest.ContentTypeHeader)
        is_image_url = "image" in header if header else False
        self.yesButton.setEnabled(is_image_url)