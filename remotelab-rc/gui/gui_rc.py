import numpy as np
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QDesktopServices

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.model_rc import RCModel
from core.csv_exporter import save_csv
from core.serial_manager import SerialManager
from app_config import APP_TITLE, APP_VERSION, GITHUB_URL, WINDOW_TITLE
from app_config import WINDOW_WIDTH, WINDOW_HEIGHT
from app_config import RESISTANCE_VALUES, CAPACITANCE_VALUES


class RCVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        try:
            with open("gui/dark_theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("No se pudo aplicar el tema:", e)

        self.model = RCModel()
        self.allow_plot = True
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plot_timer)
        self.plot_timer.start(100)

        self.serial_manager = SerialManager()

        self.modo_label = QLabel("")  # Inicialmente vacío

        logo = QLabel()
        logo.setPixmap(QPixmap("gui/udemm_logo.png").scaledToHeight(60, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel(APP_TITLE)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignLeft)

        github_button = QPushButton()
        github_button.setIcon(QIcon("assets/github_icon.png"))
        github_button.setIconSize(QSize(36, 36))
        github_button.setToolTip("Ver en GitHub")
        github_button.setFixedSize(40, 40)
        github_button.setCursor(Qt.PointingHandCursor)
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))

        version_label = QLabel(APP_VERSION)
        version_label.setStyleSheet("font-size: 12px; color: white;")
        version_label.setAlignment(Qt.AlignVCenter)

        right_layout = QHBoxLayout()
        right_layout.addWidget(github_button)
        right_layout.addWidget(version_label)
        right_layout.setAlignment(Qt.AlignRight)

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(right_layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.r_input = QComboBox()
        self.c_input = QComboBox()
        self.r_input.addItems([str(r) for r in RESISTANCE_VALUES])
        self.c_input.addItems([str(c) for c in CAPACITANCE_VALUES])

        self.port_selector = QComboBox()
        self.refresh_ports()

        self.refresh_button = QPushButton("Actualizar COMs")
        self.connect_button = QPushButton("Conectar")
        self.charge_button = QPushButton("Cargar")
        self.discharge_button = QPushButton("Descargar")
        self.save_button = QPushButton("Guardar CSV")

        self.charge_button.setVisible(False)
        self.discharge_button.setVisible(False)
        self.save_button.setVisible(False)

        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.toggle_serial_connection)
        self.save_button.clicked.connect(self.export_csv)
        self.charge_button.clicked.connect(self.iniciar_carga)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("R (Ω):"))
        controls_layout.addWidget(self.r_input)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(QLabel("C (µF):"))
        controls_layout.addWidget(self.c_input)
        controls_layout.addSpacing(30)
        controls_layout.addWidget(QLabel("Puerto:"))
        controls_layout.addWidget(self.port_selector)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.connect_button)
        controls_layout.addWidget(self.charge_button)
        controls_layout.addWidget(self.discharge_button)
        controls_layout.addWidget(self.save_button)
        controls_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)

    def refresh_ports(self):
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_serial(self):
        port = self.port_selector.currentText()
        if self.serial_manager.connect(port):
            print(f"✅ Conectado a {port}")
            self.charge_button.setVisible(True)
            self.discharge_button.setVisible(False)
            self.save_button.setVisible(False)
            self.connect_button.setText("Desconectar")
            self.port_selector.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.serial_manager.read_lines(self.handle_serial_line)
        else:
            print("❌ Falló la conexión serie")
            self.charge_button.setVisible(False)
            self.discharge_button.setVisible(False)
            self.save_button.setVisible(False)

    def disconnect_serial(self):
        self.serial_manager.disconnect()
        print("🔌 Desconectado del puerto serie")
        self.charge_button.setVisible(False)
        self.discharge_button.setVisible(False)
        self.save_button.setVisible(False)
        self.connect_button.setText("Conectar")
        self.port_selector.setEnabled(True)
        self.refresh_button.setEnabled(True)

    def toggle_serial_connection(self):
        if self.connect_button.text() == "Conectar":
            self.connect_serial()
        else:
            self.disconnect_serial()

    def plot(self, time_data, vc_data, label_real="Vc Real"):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor("#121212")
        ax.set_facecolor("#121212")

        ax.plot(time_data, vc_data, label=label_real, color="red")
        if len(self.model.vc_ideal_data) == len(time_data):
            ax.plot(time_data, self.model.vc_ideal_data, label="Vc Ideal", color="white", linestyle="--")

        ax.set_xlabel("Tiempo (ms)", color="white")
        ax.set_ylabel("Tensión (V)", color="white")

        # Mostrar el título solo si hay texto definido
        titulo = self.modo_label.text()
        if titulo:
             ax.set_title(titulo, color="#3399FF", fontsize=11)


        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
        ax.legend(facecolor="#1e1e1e", edgecolor="white", labelcolor='white')
        ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def export_csv(self):
        time_data, vc_data, _ = self.model.get_data()
        if not time_data:
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV Files (*.csv)")
        if file_name:
            save_csv(file_name, time_data, vc_data, [0] * len(vc_data))

    def handle_serial_line(self, line):
        print(f"⬅️ Recibido: {line}")
        if line == "END":
            self.allow_plot = False
            self.charge_button.setVisible(False)
            self.discharge_button.setVisible(True)
            self.save_button.setVisible(True)
            self.plot(self.model.time_data, self.model.vc_data, label_real="Vc Real")
        else:
            try:
                t_str, vc_str, vr_str = line.split(",")
                t = float(t_str)
                vc = float(vc_str)
                vr = float(vr_str)
                self.model.time_data.append(t)
                self.model.vc_data.append(vc)
                self.model.vr_data.append(vr)

                R = self.model.r
                C = self.model.c * 1e-6
                Vin = 3.3
                t_sec = t / 1000.0
                tau = R * C
                vc_ideal = Vin * (1 - np.exp(-t_sec / tau))
                self.model.vc_ideal_data.append(vc_ideal)

            except Exception as e:
                print(f"❌ Error al parsear línea: {line} — {e}")

    def iniciar_carga(self):
        r = float(self.r_input.currentText())
        c = float(self.c_input.currentText())
        modo = 0  # 0 = carga
        self.allow_plot = True
        command = f"START,{r},{c},{modo}"
        self.model.reset()
        self.model.set_params(r, c)
        self.serial_manager.send_command(command)
        self.modo_label.setText("Modo: Carga")  # Se mostrará como título del gráfico

    def update_plot_timer(self):
        if self.allow_plot:
            self.plot(self.model.time_data, self.model.vc_data, label_real="Vc Real")





