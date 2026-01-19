#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "HeartRateSensor.h"
#include <math.h>

MAX30105 particleSensor;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;
const float ALPHA = 0.75;
static bool hrSensorAvailable = false;

static int computeSimulatedHeartRate(float temperature) {
    // Si la temperatura es NAN, usar temperatura normal de bovino
    float t = isnan(temperature) ? 38.6 : temperature;
    int basePulse = 70;
    
    // FISIOLOGÍA BOVINA:
    // Temp normal: 38.0-39.3°C → FC normal: 60-80 BPM
    // Fiebre: >39.5°C → Taquicardia: 85-120 BPM
    // Hipotermia: <37.5°C → Bradicardia: 48-60 BPM
    
    if (t >= 40.0) {
        // Fiebre alta: taquicardia severa
        basePulse = 100 + (int)((t - 40.0) * 20); // 100-120 BPM
        if (basePulse > 120) basePulse = 120;
    } else if (t >= 39.5 && t < 40.0) {
        // Fiebre moderada: taquicardia
        basePulse = 85 + (int)((t - 39.5) * 30); // 85-100 BPM
    } else if (t >= 38.0 && t < 39.5) {
        // Temperatura normal: frecuencia cardíaca normal
        basePulse = 60 + (int)((t - 38.0) * 13.3); // 60-80 BPM
    } else if (t >= 37.5 && t < 38.0) {
        // Hipotermia leve: bradicardia leve
        basePulse = 55 + (int)((t - 37.5) * 10); // 55-60 BPM
    } else {
        // Hipotermia moderada/severa: bradicardia
        basePulse = 48 + (int)((t - 36.0) * 4.7); // 48-55 BPM
        if (basePulse < 48) basePulse = 48;
    }
    
    // Variación aleatoria pequeña para realismo (±3 BPM)
    return basePulse + random(-3, 4);
}

bool setupHeartRateSensor() {
    if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
        Serial.println("⚠️ El sensor MAX30105 no se pudo encontrar.");
        Serial.println("⚠️ Se usarán valores simulados de pulsaciones.");
        hrSensorAvailable = false;
        beatAvg = 60; // Valor por defecto
        return false;
    }
    Serial.println("✅ Sensor MAX30105 encontrado!");
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    hrSensorAvailable = true;
    return true;
}

void measureHeartRate(float temperature) {
    if (!hrSensorAvailable) {
        beatAvg = computeSimulatedHeartRate(temperature);
        return;
    }
    
    long irValue = particleSensor.getIR();
    bool updated = false;
    if (checkForBeat(irValue)) {
        long delta = millis() - lastBeat;
        lastBeat = millis();
        beatsPerMinute = 60 / (delta / 1000.0);
        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;
            beatAvg = 0;
            for (byte x = 0; x < RATE_SIZE; x++)
                beatAvg += rates[x];
            beatAvg /= RATE_SIZE;
            beatAvg = (int)(ALPHA * beatAvg + (1.0 - ALPHA) * beatsPerMinute);
            updated = true;
        }
    }
    // Fallback si no se actualizaron latidos recientemente o beatAvg<=0
    if (!updated || beatAvg <= 0) {
        // Si han pasado más de 5s sin latidos, usa simulación
        if (lastBeat == 0 || (millis() - lastBeat) > 5000) {
            beatAvg = computeSimulatedHeartRate(temperature);
        }
    }
}

int getHeartRate() {
    return beatAvg;
}

bool isSensorAvailable() {
    return hrSensorAvailable;
}
