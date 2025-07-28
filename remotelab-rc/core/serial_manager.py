import serial
import threading

class SerialManager:
    def __init__(self):
        self.serial = None
        self.thread = None
        self.running = False

    def connect(self, port, baudrate=115200):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            return True
        except serial.SerialException as e:
            print(f"Error abriendo el puerto serie: {e}")
            return False

    def disconnect(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send_command(self, command):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write((command + "\n").encode())
                print(f"➡️ Enviado: {command}")
            except Exception as e:
                print(f"Error enviando comando: {e}")

    def read_lines(self, callback):
        def run():
            while self.running:
                try:
                    if self.serial.in_waiting:
                        line = self.serial.readline().decode().strip()
                        if line:
                            callback(line)
                except Exception as e:
                    print(f"Error leyendo datos: {e}")
        self.running = True
        self.thread = threading.Thread(target=run)
        self.thread.start()
