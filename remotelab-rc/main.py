""" from PyQt5.QtWidgets import QApplication
import sys
from gui.gui_rc import RCVisualizer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RCVisualizer()
    window.show()
    sys.exit(app.exec_())
 """

from gui.rc_controller import RCController


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    controller = RCController()
    controller.view.show()
    sys.exit(app.exec_())
