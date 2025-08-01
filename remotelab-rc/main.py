
from gui.rc_controller import RCController  # afuera, como debe ser

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    controller = RCController()

    def on_close(event):
        controller.disconnect_serial()
        print("Aplicación cerrada correctamente.")
        event.accept()

    controller.view.closeEvent = on_close

    controller.view.show()
    sys.exit(app.exec_())

