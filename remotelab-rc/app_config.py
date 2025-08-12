# app_config.py

# Texto que aparece en la barra de título de la ventana
WINDOW_TITLE = "remoteLab-RC- UdeMM"

APP_TITLE = "FACULTAD DE INGENIERÍA - FÍSICA 1\nCARGA Y DESCARGA DE CAPACITOR"
# v1.00.1 Se agrego PING_RC para asegurar la conexion al com
# v1.02.0 Se agrego un tiempo de espera "DISCHARGE_WAIT_MS" al conectar antes de mande el  PING_RC para asegurar el sincronismo.

APP_VERSION = "v1.02.0"
GITHUB_URL = "https://github.com/theinsideshine/remotelab-rc/tree/master/remotelab-rc"

# Valores desplegables para los combos
RESISTANCE_VALUES = [10000.0,20000.0]  # en ohms
CAPACITANCE_VALUES = [ 1000,1330,1470,330, 470]           # en microfaradios


# Tamaño fijo de la ventana principal (ancho, alto)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# ⏳ Tiempo de espera antes de enviar PING_RC (ms)
DISCHARGE_WAIT_MS = 9_000   # 10 s por defecto