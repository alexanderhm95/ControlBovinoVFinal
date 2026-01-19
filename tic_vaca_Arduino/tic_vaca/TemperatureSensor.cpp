#include <OneWire.h>
#include <DallasTemperature.h>
#include <math.h>
#include "TemperatureSensor.h"

const int oneWireBus = 4;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

static bool tempSensorAvailable = false;
float lastValidTemp = 38.5; // Temperatura normal de bovino
bool setupTemperatureSensor() {
    sensors.begin();
    
    // Verificar si hay dispositivos conectados
    int deviceCount = sensors.getDeviceCount();
    
    if (deviceCount == 0) {
        Serial.println("⚠️ Sensor DS18B20 no encontrado en el pin 4");
        Serial.println("⚠️ Se usarán temperaturas simuladas (38-39°C)");
        tempSensorAvailable = false;
        return false;
    }
    
    Serial.print("✅ Sensor DS18B20 encontrado! Dispositivos: ");
    Serial.println(deviceCount);
    tempSensorAvailable = true;
    return true;
}

float getTemperature() {
    if (!tempSensorAvailable) {
        // Sensor no disponible: devolver NAN para indicar lectura inválida
        Serial.println("⚠️ Temperatura no disponible: sensor DS18B20 desconectado");
        return NAN;
    }
    
    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);
    
    // Validar lectura: DEVICE_DISCONNECTED_C (-127) u otros valores fuera de rango
    if (temp < -55 || temp > 85) {
        Serial.print("⚠️ Lectura inválida del sensor: ");
        Serial.print(temp);
        Serial.println("°C - Se omitirá la temperatura (N/D)");
        return NAN;
    }
    // Retornar lectura real sin offset
    lastValidTemp = temp;
    return lastValidTemp;
}

bool isTemperatureSensorAvailable() {
    return tempSensorAvailable;
}
