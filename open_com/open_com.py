import serial
import time

PORT = "COM6"     # cambiar al tuyo
BAUD = 115200
PING_TIMEOUT = 1  # segundos para esperar respuesta al PING_RC
LOOP_DELAY = 10   # segundos entre abrir/cerrar puerto

while True:
    # Abrir el puerto
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    time.sleep(0.5)  # dejar llegar datos iniciales

    # Leer datos iniciales
    data = ser.read_all().decode(errors="ignore")

    # Verificar si hubo reinicio
    if "rst:" in data or "ESP-ROM:" in data or "boot:" in data:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠ Reinicio detectado")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] ✅ Sin reinicio → enviando PING_RC")
        ser.write(b"PING_RC\n")

        # Esperar respuesta
        t0 = time.time()
        respuesta = ""
        while time.time() - t0 < PING_TIMEOUT:
            parte = ser.read_all().decode(errors="ignore")
            if parte:
                respuesta += parte
                break  # primera respuesta recibida

        if respuesta.strip():
            print(f"   [RX] {respuesta.strip()}")
        else:
            print("   ⚠ Sin respuesta al PING_RC")

    ser.close()
    time.sleep(LOOP_DELAY)

