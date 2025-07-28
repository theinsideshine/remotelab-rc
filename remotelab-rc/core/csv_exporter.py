import csv

def save_csv(filename, time_data, vc_data, vr_data):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tiempo (ms)", "Vc (V)", "Vr (V)"])
        for t, vc, vr in zip(time_data, vc_data, vr_data):
            writer.writerow([t, vc, vr])
