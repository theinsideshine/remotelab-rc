import csv

from PyQt5.QtWidgets import QFileDialog

def save_csv(time_data, vc_data, vr_data, vc_ideal_data):
    if not time_data or not vc_data:
        print("No hay datos para guardar.")
        return

    file_path, _ = QFileDialog.getSaveFileName(
        None, "Guardar archivo CSV", "", "CSV Files (*.csv)"
    )

    if not file_path:
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Tiempo_ms;VC_V;VR_V;VC_Ideal\n")
            for t, vc, vr, vi in zip(time_data, vc_data, vr_data, vc_ideal_data):
                line = f"{int(t)};{format(vc, '.3f').replace('.', ',')};{format(vr, '.3f').replace('.', ',')};{format(vi, '.3f').replace('.', ',')}\n"
                f.write(line)
        print(f"Archivo guardado en {file_path}")
    except Exception as e:
        print(f"Error al guardar CSV: {e}")

