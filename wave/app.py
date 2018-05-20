from PyQt5.Qt import *  # All classes prefaced by Q (ex: QApplication)
from .main_window import MainWindow
from .model import Model

import sys


def main():
    app = QApplication([sys.argv])  # expects list of strings.
    model = Model()
    main_win = MainWindow(model)
    app.exec()
