from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class LoadSaveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Load Save State?")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(
            "We found a non-finished whittling,  would you like to continue your last project?"
        )
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class ErrorDialog(QDialog):
    def __init__(self, error: str, error_reason: str, extra_info="", parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Error Encountered!")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setCenterButtons(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)

        error_message = QLabel(error)
        error_message.setStyleSheet("font-weight: bold")
        message_text = QLabel(error_reason)
        self.layout.addWidget(error_message)
        self.layout.addWidget(message_text)
        if extra_info:
            self.layout.addWidget(QLabel(extra_info))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class ActionCompleteDialog(QDialog):
    def __init__(self, action: str, action_message: str, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle(f"{action} Completed!")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setCenterButtons(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)

        completed_message = QLabel(f"{action} Completed!")
        completed_message.setStyleSheet("font-weight: bold")
        message_text = QLabel(action_message)
        self.layout.addWidget(completed_message)
        self.layout.addWidget(message_text)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
