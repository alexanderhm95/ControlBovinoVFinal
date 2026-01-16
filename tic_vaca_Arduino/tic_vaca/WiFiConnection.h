#ifndef WIFICONNECTION_H
#define WIFICONNECTION_H

void connectToWiFi();
void startConfigPortal();
bool isWiFiConfigured();
void saveWiFiCredentials(String ssid, String password);
void loadWiFiCredentials();
bool checkInternetConnection();
void monitorConnectivity();

#endif
