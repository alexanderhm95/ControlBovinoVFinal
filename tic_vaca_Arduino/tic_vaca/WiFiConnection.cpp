#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <HTTPClient.h>
#include "WiFiConnection.h"

// Variables para el portal de configuración
WebServer server(80);
DNSServer dnsServer;
Preferences preferences;

// Credenciales por defecto (se cargarán desde la memoria)
String stored_ssid = "";
String stored_password = "";

// Variables para monitoreo de conectividad
unsigned long lastInternetCheck = 0;
const unsigned long internetCheckInterval = 30000; // Verificar cada 30 segundos
int consecutiveFailures = 0;
const int maxConsecutiveFailures = 3; // Máximo 3 fallos consecutivos antes de abrir portal

const char* ap_ssid = "CollarSalome_Config";
const char* ap_password = "12345678";

// Página HTML para el portal de configuración
const char* configPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <title>Configuracion WiFi - Collar Vaca</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f0f0f0; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .alert { padding: 15px; margin: 15px 0; border-radius: 5px; }
        .alert-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-info { background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; background-color: #4CAF50; color: white; padding: 14px; margin: 8px 0; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background-color: #45a049; }
        .network-list { margin: 20px 0; }
        .network-item { padding: 10px; border: 1px solid #ddd; margin: 5px 0; border-radius: 4px; cursor: pointer; background: #f9f9f9; }
        .network-item:hover { background: #e9e9e9; }
        .signal-strength { float: right; font-weight: bold; }
        .status-info { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .password-container { position: relative; display: inline-block; width: 100%; }
        .password-toggle { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 18px; color: #666; user-select: none; }
        .password-toggle:hover { color: #333; }
        .show-password-checkbox { margin: 10px 0; }
        .show-password-checkbox label { display: flex; align-items: center; cursor: pointer; font-size: 14px; color: #666; }
        .show-password-checkbox input[type="checkbox"] { margin-right: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐄 Collar Vaca Sofia</h1>
        <h2>Configuracion WiFi</h2>
        
        <div class="alert alert-warning">
            <strong>⚠️ Portal de Configuración Activo</strong><br>
            El collar no puede conectarse a internet. Esto puede deberse a:
            <ul style="margin: 10px 0;">
                <li>Problemas con la red WiFi actual</li>
                <li>Cambio de contraseña del router</li>
                <li>Problemas con el proveedor de internet</li>
                <li>Señal WiFi débil o intermitente</li>
            </ul>
        </div>
        
        <div class="network-list">
            <h3>Redes WiFi disponibles:</h3>
            <div id="networks">Escaneando redes...</div>
        </div>
        
        <form action="/save" method="POST">
            <label for="ssid">Nombre de la red (SSID):</label>
            <input type="text" id="ssid" name="ssid" required>
            
            <label for="password">Contraseña:</label>
            <div class="password-container">
                <input type="password" id="password" name="password" required>
                <span class="password-toggle" onclick="togglePassword()" id="toggleIcon">👁️</span>
            </div>
            
            <div class="show-password-checkbox">
                <label>
                    <input type="checkbox" id="showPassword" onchange="togglePasswordCheckbox()">
                    Mostrar contraseña
                </label>
            </div>
            
            <input type="submit" value="Guardar y Conectar">
        </form>
        
        <div class="alert alert-info">
            <strong>💡 Consejos:</strong><br>
            • Asegúrate de que la red tenga acceso a internet<br>
            • Verifica que la contraseña sea correcta<br>
            • Confirma que la señal WiFi sea fuerte<br>
            • El collar verificará la conectividad automáticamente
        </div>
        
        <p style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
            Sistema de Monitoreo de Ganado v2.0<br>
            Auto-diagnóstico de conectividad habilitado
        </p>
    </div>
    
    <script>
        function selectNetwork(ssid) {
            document.getElementById('ssid').value = ssid;
        }
        
        function togglePassword() {
            const passwordField = document.getElementById('password');
            const toggleIcon = document.getElementById('toggleIcon');
            const showPasswordCheckbox = document.getElementById('showPassword');
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                toggleIcon.textContent = '🙈';
                showPasswordCheckbox.checked = true;
            } else {
                passwordField.type = 'password';
                toggleIcon.textContent = '👁️';
                showPasswordCheckbox.checked = false;
            }
        }
        
        function togglePasswordCheckbox() {
            const passwordField = document.getElementById('password');
            const toggleIcon = document.getElementById('toggleIcon');
            const showPasswordCheckbox = document.getElementById('showPassword');
            
            if (showPasswordCheckbox.checked) {
                passwordField.type = 'text';
                toggleIcon.textContent = '🙈';
            } else {
                passwordField.type = 'password';
                toggleIcon.textContent = '👁️';
            }
        }
        
        // Cargar redes disponibles
        fetch('/scan')
            .then(response => response.json())
            .then(data => {
                let networksHtml = '';
                data.networks.forEach(network => {
                    let signalIcon = '';
                    let signalClass = '';
                    if (network.rssi > -50) {
                        signalIcon = '📶📶📶';
                        signalClass = 'color: green;';
                    } else if (network.rssi > -70) {
                        signalIcon = '📶📶';
                        signalClass = 'color: orange;';
                    } else if (network.rssi > -80) {
                        signalIcon = '📶';
                        signalClass = 'color: red;';
                    } else {
                        signalIcon = '📶';
                        signalClass = 'color: red;';
                    }
                    
                    let secureIcon = network.secure ? '🔒' : '🔓';
                    
                    networksHtml += `<div class="network-item" onclick="selectNetwork('${network.ssid}')">
                        ${secureIcon} ${network.ssid} 
                        <span class="signal-strength" style="${signalClass}">${signalIcon} ${network.rssi}dBm</span>
                    </div>`;
                });
                if (networksHtml === '') {
                    networksHtml = '<div style="text-align: center; color: #666;">No se encontraron redes WiFi</div>';
                }
                document.getElementById('networks').innerHTML = networksHtml;
            })
            .catch(error => {
                document.getElementById('networks').innerHTML = '<div style="text-align: center; color: red;">Error al escanear redes</div>';
            });
    </script>
</body>
</html>
)rawliteral";

void loadWiFiCredentials() {
    preferences.begin("wifi", false);
    stored_ssid = preferences.getString("ssid", "");
    stored_password = preferences.getString("password", "");
    preferences.end();
}

void saveWiFiCredentials(String ssid, String password) {
    preferences.begin("wifi", false);
    preferences.putString("ssid", ssid);
    preferences.putString("password", password);
    preferences.end();
    stored_ssid = ssid;
    stored_password = password;
}

bool isWiFiConfigured() {
    return (stored_ssid.length() > 0 && stored_password.length() > 0);
}

void handleRoot() {
    server.send(200, "text/html", configPage);
}

void handleScan() {
    String json = "{\"networks\":[";
    int n = WiFi.scanNetworks();
    
    for (int i = 0; i < n; i++) {
        if (i > 0) json += ",";
        json += "{";
        json += "\"ssid\":\"" + WiFi.SSID(i) + "\",";
        json += "\"rssi\":" + String(WiFi.RSSI(i)) + ",";
        json += "\"secure\":" + String(WiFi.encryptionType(i) != WIFI_AUTH_OPEN);
        json += "}";
    }
    json += "]}";
    
    server.send(200, "application/json", json);
}

void handleSave() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    
    if (ssid.length() > 0) {
        saveWiFiCredentials(ssid, password);
        
        String html = "<!DOCTYPE html><html><head><title>Guardado</title><meta http-equiv='refresh' content='5;url=/'></head>";
        html += "<body style='font-family: Arial; text-align: center; margin-top: 50px;'>";
        html += "<h1>✅ Credenciales guardadas</h1>";
        html += "<p>Intentando conectar a: <strong>" + ssid + "</strong></p>";
        html += "<p>El dispositivo se reiniciará en 5 segundos...</p>";
        html += "</body></html>";
        
        server.send(200, "text/html", html);
        
        delay(2000);
        ESP.restart();
    } else {
        server.send(400, "text/html", "Error: SSID no puede estar vacío");
    }
}

void startConfigPortal() {
    Serial.println("Iniciando portal de configuración WiFi...");
    
    // Configurar punto de acceso
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ap_ssid, ap_password);
    
    Serial.print("Portal WiFi iniciado: ");
    Serial.println(ap_ssid);
    Serial.print("Contraseña: ");
    Serial.println(ap_password);
    Serial.print("IP del portal: ");
    Serial.println(WiFi.softAPIP());
    
    // Configurar DNS para redirigir todas las consultas al ESP32
    dnsServer.start(53, "*", WiFi.softAPIP());
    
    // Configurar rutas del servidor web
    server.on("/", handleRoot);
    server.on("/scan", handleScan);
    server.on("/save", HTTP_POST, handleSave);
    
    // Redirigir cualquier otra página al portal
    server.onNotFound([]() {
        server.sendHeader("Location", "http://" + WiFi.softAPIP().toString(), true);
        server.send(302, "text/plain", "");
    });
    
    server.begin();
    Serial.println("Servidor web iniciado");
    Serial.println("Conectate a la red 'CollarVaca_Config' y ve a cualquier página web");
    
    // Mantener el portal activo hasta que se configuren las credenciales
    while (true) {
        dnsServer.processNextRequest();
        server.handleClient();
        delay(100);
    }
}

void connectToWiFi() {
    loadWiFiCredentials();
    
    if (!isWiFiConfigured()) {
        Serial.println("No hay credenciales WiFi guardadas. Iniciando portal de configuración...");
        startConfigPortal();
        return;
    }
    
    Serial.print("Conectando a WiFi: ");
    Serial.println(stored_ssid);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(stored_ssid.c_str(), stored_password.c_str());
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" ¡Conectado a WiFi!");
        Serial.print("IP asignada: ");
        Serial.println(WiFi.localIP());
        Serial.print("MAC Address: ");
        Serial.println(WiFi.macAddress());
        
        // Verificar conectividad a internet
        if (checkInternetConnection()) {
            Serial.println("✅ Conexión a internet verificada");
            consecutiveFailures = 0; // Resetear contador de fallos
        } else {
            Serial.println("⚠️ Conectado a WiFi pero sin acceso a internet");
            consecutiveFailures++;
        }
    } else {
        Serial.println(" No se pudo conectar a WiFi. Iniciando portal de configuración...");
        startConfigPortal();
    }
}

bool checkInternetConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi no conectado, no se puede verificar internet");
        return false;
    }
    
    HTTPClient http;
    http.begin("http://httpbin.org/get"); // Servicio simple para verificar conectividad
    http.setTimeout(5000); // Timeout de 5 segundos
    
    int httpCode = http.GET();
    http.end();
    
    if (httpCode > 0) {
        Serial.println("✅ Conexión a internet OK");
        return true;
    } else {
        Serial.print("❌ Error de conexión a internet. Código: ");
        Serial.println(httpCode);
        return false;
    }
}

void monitorConnectivity() {
    unsigned long currentMillis = millis();
    
    // Verificar conectividad solo cada cierto intervalo
    if (currentMillis - lastInternetCheck >= internetCheckInterval) {
        lastInternetCheck = currentMillis;
        
        // Verificar WiFi primero
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("🔄 WiFi desconectado. Reintentando conexión...");
            connectToWiFi();
            return;
        }
        
        // Verificar internet
        if (!checkInternetConnection()) {
            consecutiveFailures++;
            Serial.print("⚠️ Fallo de internet #");
            Serial.print(consecutiveFailures);
            Serial.print(" de ");
            Serial.println(maxConsecutiveFailures);
            
            if (consecutiveFailures >= maxConsecutiveFailures) {
                Serial.println("🚨 Demasiados fallos de conectividad. Iniciando portal de reconfiguración...");
                
                // Mostrar mensaje informativo
                Serial.println("═══════════════════════════════════════");
                Serial.println("  PROBLEMA DE CONECTIVIDAD DETECTADO");
                Serial.println("═══════════════════════════════════════");
                Serial.println("• WiFi conectado pero sin acceso a internet");
                Serial.println("• Posibles causas:");
                Serial.println("  - Router sin conexión a internet");
                Serial.println("  - Problemas con el proveedor de internet");
                Serial.println("  - Configuración de red incorrecta");
                Serial.println("• Iniciando portal para reconfigurar...");
                Serial.println("═══════════════════════════════════════");
                
                // Reiniciar el portal de configuración
                WiFi.disconnect();
                delay(1000);
                startConfigPortal();
            }
        } else {
            // Conexión exitosa, resetear contador
            if (consecutiveFailures > 0) {
                Serial.println("✅ Conectividad restaurada");
                consecutiveFailures = 0;
            }
        }
    }
}
