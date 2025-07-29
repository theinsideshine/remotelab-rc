from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QPixmap, QIcon, QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import QTimer




from app_config import (
    APP_TITLE, APP_VERSION, GITHUB_URL, WINDOW_TITLE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    RESISTANCE_VALUES, CAPACITANCE_VALUES
)


class RCView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Inicialización del modelo y serial_manager como None, lo asigna el controlador
        self.model = None
        self.serial_manager = None

        try:
            with open("gui/dark_theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("No se pudo aplicar el tema:", e)

        self.allow_plot = True

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
        self.r_input.addItems([str(r) for r in RESISTANCE_VALUES])
        self.c_input = QComboBox()
        self.c_input.addItems([str(c) for c in CAPACITANCE_VALUES])

        self.port_selector = QComboBox()
        self.refresh_button = QPushButton("Actualizar COMs")
        self.connect_button = QPushButton("Conectar")
        self.disconnect_button = QPushButton("Desconectar")
        self.charge_button = QPushButton("Cargar")
        self.discharge_button = QPushButton("Descargar")
        self.save_button = QPushButton("Guardar CSV")

        self.charge_button.setVisible(False)
        self.discharge_button.setVisible(False)
        self.save_button.setVisible(False)
        self.disconnect_button.setVisible(False)  # inicia oculto

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
        controls_layout.addWidget(self.disconnect_button)
        controls_layout.addWidget(self.charge_button)
        controls_layout.addWidget(self.discharge_button)
        controls_layout.addWidget(self.save_button)
        controls_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)

        # Al final del __init__ de RCView
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plot_timer)
        self.plot_timer.start(100)

    def plot(self, time_data, vc_data, label_real="Vc Real"):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor("#121212")
        ax.set_facecolor("#121212")

        ax.plot(time_data, vc_data, label=label_real, color="red")
        if self.model and len(self.model.vc_ideal_data) == len(time_data):
            ax.plot(time_data, self.model.vc_ideal_data, label="Vc Ideal", color="white", linestyle="--")

        ax.set_xlabel("Tiempo (ms)", color="white")
        ax.set_ylabel("Tensión (V)", color="white")

        titulo = self.modo_label.text()
        if titulo:
            ax.set_title(titulo, color="#3399FF", fontsize=11)

        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
        ax.legend(facecolor="#1e1e1e", edgecolor="white", labelcolor='white')
        ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def update_plot_timer(self):
        if self.allow_plot and self.model:
            self.plot(self.model.time_data, self.model.vc_data, label_real="Vc Real")

    def set_state_message(self, state: str):
        mensajes = {
            "not_connected": "",
            "idle_charge": "Listo para cargar",
            "charging": "Cargando",
            "idle_discharge": "Carga finalizada",
            "discharging": "Descargando",
            "wait_data": "Esperando datos...",
        }
        self.modo_label.setText(mensajes.get(state, ""))

    def update_buttons(self, state: str):
        if state == "not_connected":
            self.connect_button.setVisible(True)
            self.disconnect_button.setVisible(False)
            self.charge_button.setVisible(False)
            self.discharge_button.setVisible(False)
            self.save_button.setVisible(False)

        elif state == "idle_charge":
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.charge_button.setVisible(True)
            self.discharge_button.setVisible(False)
            self.save_button.setVisible(False)

        elif state == "charging":
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.charge_button.setVisible(True)
            self.discharge_button.setVisible(False)
            self.save_button.setVisible(False)

        elif state == "idle_discharge":
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.charge_button.setVisible(False)
            self.discharge_button.setVisible(True)
            self.save_button.setVisible(True)

        elif state == "discharging":
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.charge_button.setVisible(False)
            self.discharge_button.setVisible(True)
            self.save_button.setVisible(False)



