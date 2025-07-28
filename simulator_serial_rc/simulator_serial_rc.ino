// simulador_RC_serial.ino
// Simula experimento RC enviando datos reales por Serial sin usar hardware

/**
 ESP32-S3DEVKITC-1_V1.1
 * C:\Users\ptavolaro\AppData\Local\arduino\sketches
*/

struct DataPoint {
  float t_ms;
  float vc;
  float vr;
};

// Archivos de datos
DataPoint simDataCharge[] = {
#include "simdata_charge.inl"
};

DataPoint simDataDischarge[] = {
#include "simdata_discharge.inl"
};

// Longitudes
const int simDataChargeLength = sizeof(simDataCharge) / sizeof(DataPoint);
const int simDataDischargeLength = sizeof(simDataDischarge) / sizeof(DataPoint);

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Simulador RC Serie - Version V2.00");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line.startsWith("START")) {
      int modo = 0;

      // Intenta extraer el modo como el último parámetro
      int lastComma = line.lastIndexOf(',');
      if (lastComma > 0) {
        String lastPart = line.substring(lastComma + 1);
        modo = lastPart.toInt();
      }

      Serial.println("BEGIN");

      DataPoint* dataArray = (modo == 1) ? simDataDischarge : simDataCharge;
      int length = (modo == 1) ? simDataDischargeLength : simDataChargeLength;

      for (int i = 0; i < length; i++) {
        Serial.printf("%.1f,%.3f,%.3f\n", dataArray[i].t_ms, dataArray[i].vc, dataArray[i].vr);
        delay(50);
      }

      Serial.println("END");
    }
  }
}
