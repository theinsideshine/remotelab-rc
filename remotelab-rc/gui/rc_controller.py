import serial.tools.list_ports
from core.model_rc import RCModel
from core.csv_exporter import save_csv
from core.serial_manager import SerialManager
from gui.rc_view import RCView
import numpy as np
import time  # 👈 necesario para timeout




class RCController:
    def __init__(self):
        self.model = RCModel()
        self.serial_manager = SerialManager()
        self.view = RCView()
        self.view.model = self.model
        self.state = "not_connected"
        self.view.set_state_message(self.state)
        self.view.update_buttons(self.state)



        self.setup_connections()
        self.refresh_ports()

    def setup_connections(self):
        self.view.connect_button.clicked.connect(self.connect_serial)
        self.view.disconnect_button.clicked.connect(self.disconnect_serial)  # ← AGREGAR ESTA
        self.view.charge_button.clicked.connect(self.send_charge_command)
        self.view.discharge_button.clicked.connect(self.send_discharge_command)
        self.view.save_button.clicked.connect(self.save_to_csv)
        self.view.r_input.currentIndexChanged.connect(self.update_model_parameters)
        self.view.c_input.currentIndexChanged.connect(self.update_model_parameters)
        self.view.refresh_button.clicked.connect(self.refresh_ports)


    def refresh_ports(self):
        self.view.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.view.port_selector.addItem(port.device)

    def connect_serial(self):
        port = self.view.port_selector.currentText()
        success = self.serial_manager.connect(port)
        if not success:
            print(f"❌ No se pudo conectar a {port}")
            return

        print(f"🔌 Conectado a {port}, verificando dispositivo...")
        self.serial_manager.send_command("PING_RC")

        # Esperar respuesta por un tiempo (ej. 1 segundo)
        ack_received = False
        start_time = time.time()
        buffer = ""

        while time.time() - start_time < 1.0:
            line = self.serial_manager.serial.readline().decode(errors="ignore").strip()
            if line:
                print(f"Recibido: {line}")
                if line.upper() == "ACK_RC":
                    ack_received = True
                    break

        if ack_received:
            print("Dispositivo verificado")
            self.state = "idle_charge"
            self.view.set_state_message(self.state)
            self.view.update_buttons(self.state)
            self.serial_manager.read_lines(self.handle_serial_data)
        else:
            print("El dispositivo conectado no respondió correctamente (esperado: ACK_RC)")
            self.serial_manager.disconnect()



    def disconnect_serial(self):
        self.serial_manager.disconnect()
        print("Desconectado del puerto serie")

        # 🔄 Volver al estado inicial
        self.state = "not_connected"
        self.view.set_state_message(self.state)
        self.view.update_buttons(self.state)
        self.view.allow_plot = False

        # 🧹 Limpiar datos del modelo
        self.model.reset()
        self.model.vc_ideal_data.clear()
        self.model.time_data.clear()
        self.model.vc_data.clear()
        self.model.vr_data.clear()

        # 🖼️ Borrar gráfico
        self.view.clear_plot()



    def send_charge_command(self):
        r = float(self.view.r_input.currentText())
        c = float(self.view.c_input.currentText())
        self.model.reset(start_from_vin=False)
        self.model.set_params(r, c)
        self.model.set_mode("charge")
        command = f"START,{r},{c},0"
        self.serial_manager.send_command(command)
        self.state = "charging"
        self.view.set_state_message(self.state)
        self.view.update_buttons(self.state)
        self.view.allow_plot = True

    def send_discharge_command(self):
        r = float(self.view.r_input.currentText())
        c = float(self.view.c_input.currentText())
        self.model.reset(start_from_vin=True)
        self.model.set_params(r, c)
        self.model.set_mode("discharge")
        command = f"START,{r},{c},1"
        self.serial_manager.send_command(command)

        self.state = "discharging"
        self.view.set_state_message(self.state)
        self.view.update_buttons(self.state)
        self.view.allow_plot = True



    def save_to_csv(self):
        save_csv(
            self.model.time_data,
            self.model.vc_data,
            self.model.vr_data,
            self.model.vc_ideal_data
        )

    def update_model_parameters(self):
        try:
            r = float(self.view.r_input.currentText())
            c = float(self.view.c_input.currentText())
            self.model.set_params(r, c)
        except ValueError:
            print("Error al actualizar R o C")

    def handle_serial_data(self, line):
        try:
            print(f"Recibido: {line.strip()}")

            if line.strip().upper() == "END":
                print("Lectura finalizada")
                if self.model.mode == "charge":
                    self.state = "finished_charge"
                else:
                    self.state = "finished_discharge"
                self.view.set_state_message(self.state)
                self.view.update_buttons(self.state)
                self.view.allow_plot = False
                self.view.plot(self.model.time_data, self.model.vc_data, label_real="Vc Real")
                return



            parts = line.split(",")
            if len(parts) != 3:
                return

            t, vc, vr = map(float, parts)
            self.model.time_data.append(t)
            self.model.vc_data.append(vc)
            self.model.vr_data.append(vr)

            r = self.model.r
            c = self.model.c * 1e-6
            vin = 3.3
            t_sec = t / 1000.0
            tau = r * c
            if self.model.mode == "charge":
                vc_ideal = vin * (1 - np.exp(-t_sec / tau))  # carga
            else:
                vc_ideal = vin * np.exp(-t_sec / tau)        # descarga

            self.model.vc_ideal_data.append(vc_ideal)

            # ❌ NO llamar update_plot_timer acá

        except Exception as e:
            print(f"⚠️ Error al parsear línea: {line} → {e}")

