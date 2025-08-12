// simulador_RC_serial.ino
// Simula experimento RC enviando datos reales por Serial sin usar hardware

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

// ---- Handshake de arranque (igual que firmware real) ----
#define BOOT_DISCHARGE_MS 6000   // 6 s (si querés 60 s, poné 60000)

bool booting = true;
unsigned long bootStart = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Simulador RC Serie - Version V2.11");

  // Marca de inicio como en el firmware real (opcional, pero útil)
  Serial.println("INI_RC");

  bootStart = millis();
}

void loop() {
  // Mientras está "descargando", NO atender comandos
  if (booting) {
    if (millis() - bootStart >= BOOT_DISCHARGE_MS) {
      Serial.println("READY");   // recién ahora queda listo
      booting = false;
    }
    return; // ignorar todo hasta que termine el boot
  }

  // ---- A partir de acá, se atienden comandos por Serial ----
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    // Comando de ping
    if (line == "PING_RC") {
      Serial.println("ACK_RC");  // mantener comportamiento existente
    }

    // Comando de experimento
    else if (line.startsWith("START")) {
      int modo = 0;

      // Extraer modo como último parámetro
      int lastComma = line.lastIndexOf(',');
      if (lastComma > 0) {
        String lastPart = line.substring(lastComma + 1);
        modo = lastPart.toInt();  // 0 = carga, 1 = descarga
      }

      Serial.println("ACK");     // ✅ Confirma recepción
      delay(100);                // Simula tiempo de preparación
      Serial.println("BEGIN");

      DataPoint* dataArray = (modo == 1) ? simDataDischarge : simDataCharge;
      int length = (modo == 1) ? simDataDischargeLength : simDataChargeLength;

      for (int i = 0; i < length; i++) {
        Serial.printf("%.1f,%.3f,%.3f\n", dataArray[i].t_ms, dataArray[i].vc, dataArray[i].vr);
        delay(50); // Simula muestreo
      }

      Serial.println("END");
    }
  }
}


