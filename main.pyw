import sys
import gamelist.mainwindow

from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = gamelist.mainwindow.GameListGUI()
    window.show()
    sys.exit(app.exec_())
