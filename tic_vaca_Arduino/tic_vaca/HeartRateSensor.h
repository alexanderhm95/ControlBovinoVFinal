#ifndef HEARTRATESENSOR_H
#define HEARTRATESENSOR_H

bool setupHeartRateSensor();
void measureHeartRate(float temperature = 38.5);
int getHeartRate();
bool isSensorAvailable();

#endif
