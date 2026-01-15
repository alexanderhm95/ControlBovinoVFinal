#include <HTTPClient.h>
#include "DataSender.h"
#include <ArduinoJson.h>

const char* serverUrl = "https://pmonitunl.vercel.app/api/arduino/monitoreo";

// Clave API para autenticación (configurable desde el header)
const char* API_KEY = "YOUR_API_KEY_HERE"; // Reemplazar con clave real

void sendDataToServer(String collarID, float temperature, String nombre_vaca, int pulsaciones, String macAddress) {
    HTTPClient http;
    
    // Configurar con timeout
    http.setTimeout(5000); // 5 segundos timeout
    
    Serial.println("\n=== ENVIANDO DATOS AL SERVIDOR ===");
    Serial.print("URL: ");
    Serial.println(serverUrl);
    
    http.begin(serverUrl);
    
    // Agregar headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("User-Agent", "ControlBovino/1.0");
    
    // Agregar autenticación con API Key
    String authHeader = "Bearer ";
    authHeader += API_KEY;
    http.addHeader("Authorization", authHeader);
    
    // Crear objeto JSON con datos
    DynamicJsonDocument jsonDoc(1024);
    jsonDoc["collar_id"] = collarID;
    jsonDoc["temperatura"] = temperature;
    jsonDoc["nombre_vaca"] = nombre_vaca;
    jsonDoc["pulsaciones"] = pulsaciones;
    jsonDoc["mac_collar"] = macAddress;
    
    // Serializar a string
    String postData;
    serializeJson(jsonDoc, postData);
    
    Serial.print("Payload: ");
    Serial.println(postData);
    
    // Enviar petición
    Serial.println("Enviando petición POST...");
    int httpResponseCode = http.POST(postData);
    
    // Procesar respuesta
    if (httpResponseCode > 0) {
        Serial.print("✅ Respuesta HTTP: ");
        Serial.println(httpResponseCode);
        
        String response = http.getString();
        Serial.print("Respuesta servidor: ");
        Serial.println(response);
        
        // Verificar si fue exitoso (200-299)
        if (httpResponseCode >= 200 && httpResponseCode < 300) {
            Serial.println("✅ Datos enviados correctamente");
        } else if (httpResponseCode == 401) {
            Serial.println("❌ Error 401: No autorizado - Verificar API Key");
        } else if (httpResponseCode == 400) {
            Serial.println("❌ Error 400: Datos inválidos");
        } else if (httpResponseCode == 500) {
            Serial.println("❌ Error 500: Error del servidor");
        } else {
            Serial.print("⚠️ Error HTTP: ");
            Serial.println(httpResponseCode);
        }
    } else {
        Serial.print("❌ Error en petición HTTP: ");
        Serial.println(httpResponseCode);
        Serial.print("Error string: ");
        Serial.println(http.errorToString(httpResponseCode));
    }
    
    http.end();
    Serial.println("=== FIN ENVÍO ===\n");
}
