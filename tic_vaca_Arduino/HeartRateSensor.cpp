#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "HeartRateSensor.h"

MAX30105 particleSensor;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;
const float ALPHA = 0.75;

void setupHeartRateSensor() {
    if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
        Serial.println("El sensor no se pudo encontrar. Por favor, revise las conexiones.");
        while (1);
    }
    Serial.println("Sensor encontrado!");
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
}

void measureHeartRate() {
    long irValue = particleSensor.getIR();
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
            beatAvg = (int)(ALPHA * beatAvg + (1.0 - ALPHA) * beatsPerMinute);// Ajuste de la media movil con un factor de suavizado ALPHA para obtener una mejor lectura
        }
    }
    
}

int getHeartRate() {
    return beatAvg;
}
