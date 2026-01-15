#include <OneWire.h>
#include <DallasTemperature.h>
#include "TemperatureSensor.h"

const int oneWireBus = 4;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

void setupTemperatureSensor() {
    sensors.begin();
}

float getTemperature() {
    sensors.requestTemperatures();
    return sensors.getTempCByIndex(0)+0.5;
}
