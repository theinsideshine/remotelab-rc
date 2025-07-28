from PyQt5.QtWidgets import QApplication
import sys
from gui.gui_rc import RCVisualizer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RCVisualizer()
    window.show()
    sys.exit(app.exec_())
