## gui_rc.py
import numpy as np
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from model_rc import RCModel
from csv_exporter import save_csv
from serial_manager import SerialManager

class RCVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador RC - UdeMM")
        self.setMinimumSize(1000, 600)
        self.resize(1000, 600)

        try:
            with open("dark_theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("No se pudo aplicar el tema:", e)

        self.model = RCModel()
        self.serial_manager = SerialManager()

        logo = QLabel()
        logo.setPixmap(QPixmap("udemm_logo.png").scaledToHeight(60, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignLeft)

        title = QLabel("FACULTAD DE INGENIERÍA - FÍSICA 1\nCARGA Y DESCARGA DE CAPACITOR")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        header_layout = QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.r_input = QLineEdit("10.0")
        self.c_input = QLineEdit("100")
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
            self.discharge_button.setVisible(True)
            self.save_button.setVisible(True)
            self.connect_button.setText("Desconectar")
            self.port_selector.setEnabled(False)
            self.refresh_button.setEnabled(False)
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
        try:
            R = float(self.r_input.text())
            C = float(self.c_input.text())
            Vin = 3.3
            t_sec = np.array(time_data) / 1000.0
            tau = R * C * 1e-6
            vc_ideal = Vin * (1 - np.exp(-t_sec / tau))
        except:
            vc_ideal = []

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor("#121212")
        ax.set_facecolor("#121212")

        ax.plot(time_data, vc_data, label=label_real, color="red")
        if len(vc_ideal) == len(vc_data):
            ax.plot(time_data, vc_ideal, label="Vc Ideal", color="white", linestyle="--")

        ax.set_xlabel("Tiempo (ms)", color="white")
        ax.set_ylabel("Tensión (V)", color="white")
        ax.set_title("Simulación RC", color="white")

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
            save_csv(file_name, time_data, vc_data, [0]*len(vc_data))
