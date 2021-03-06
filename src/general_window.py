from PyQt5.QtWidgets import (
    QMainWindow,
)

from src.constants import BACKGROUND_COLOR


class GeneralWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(BACKGROUND_COLOR)

        self.resize(1000, 600)

