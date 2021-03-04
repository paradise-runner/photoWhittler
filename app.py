import sys

from PyQt5.QtWidgets import QApplication

from src.whittler import Whittler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    whittler = Whittler()
    whittler.show()
    sys.exit(app.exec_())
