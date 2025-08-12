# sniff_serial.py
import serial, time

PORT = "COM6"         # <- cambiá
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.2)
time.sleep(0.2)

# (Opcional) forzar reset en algunos boards
try:
    ser.setDTR(False); time.sleep(0.05); ser.setDTR(True)
except Exception:
    pass

print("Leyendo...")
t0 = time.time()
while time.time() - t0 < 30:
    line = ser.readline().decode(errors="ignore").strip()
    if line:
        print(f"[RX] {line}")
ser.close()
