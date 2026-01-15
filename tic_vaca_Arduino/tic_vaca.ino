#include <Arduino.h>
#include <WiFi.h>
#include "WiFiConnection.h"
#include "TemperatureSensor.h"
#include "HeartRateSensor.h"
#include "DataSender.h"

const String COLLAR_UNO = "2";
const String nombre_vaca = "Salome";
const unsigned long printPeriod = 10000; // Tiempo para enviar los datos cada 10 seg
unsigned long previousMillis = 0;

// Pin para el botón de configuración WiFi (opcional)
const int CONFIG_BUTTON_PIN = 0; // GPIO0 (botón BOOT en muchos ESP32)
bool buttonPressed = false;
unsigned long buttonPressTime = 0;

void setup() {
    Serial.begin(9600);
    
    // Configurar pin del botón como entrada con pull-up
    pinMode(CONFIG_BUTTON_PIN, INPUT_PULLUP);
    
    // Conectar a WiFi (iniciará el portal si no hay credenciales)
    connectToWiFi();
    
    // Solo continuar si estamos conectados a WiFi
    if (WiFi.status() == WL_CONNECTED) {
        setupTemperatureSensor();
        setupHeartRateSensor();
        Serial.println("Sistema iniciado correctamente");
    }
}

void checkConfigButton() {
    // Verificar si el botón está presionado por más de 3 segundos
    if (digitalRead(CONFIG_BUTTON_PIN) == LOW) {
        if (!buttonPressed) {
            buttonPressed = true;
            buttonPressTime = millis();
        } else if (millis() - buttonPressTime > 3000) {
            Serial.println("Botón de configuración presionado. Reiniciando portal...");
            // Borrar credenciales y reiniciar
            startConfigPortal();
        }
    } else {
        buttonPressed = false;
    }
}

void loop() {
    // Verificar botón de configuración
    checkConfigButton();
    
    // Monitorear conectividad WiFi e internet
    monitorConnectivity();
    
    // Solo ejecutar el loop principal si estamos conectados a WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi desconectado. El monitoreo se encargará de la reconexión...");
        delay(5000);
        return;
    }
    
    measureHeartRate();
    
    if ((unsigned long)(millis() - previousMillis) >= printPeriod) {
        previousMillis = millis();
        float temperature = getTemperature();
        int pulsaciones = getHeartRate();
        String collarID = COLLAR_UNO;
        
        Serial.print("Collar ID=");
        Serial.print(collarID);
        Serial.print(", Temp=");
        Serial.print(temperature);
        Serial.print(", Pulsaciones=");
        Serial.print(pulsaciones);
        Serial.println();
        
        String macAddress = WiFi.macAddress();
        sendDataToServer(collarID, temperature, nombre_vaca, pulsaciones, macAddress);
    }
}
