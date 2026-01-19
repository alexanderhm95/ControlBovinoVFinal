# 🐄 Sistema de Monitoreo de Ganado - Collar Inteligente v2.0

## 📋 Descripción General
Sistema completo de monitoreo de ganado basado en ESP32 que incluye sensores de temperatura corporal y frecuencia cardíaca, con portal de configuración WiFi inteligente y monitoreo automático de conectividad a internet.

### 🏷️ Configuración Actual del Collar
- **ID del Collar**: "2"
- **Nombre de la Vaca**: "Salome"
- **Red WiFi del Portal**: "CollarSalome_Config"
- **Servidor de Datos**: https://pmonitunl.vercel.app/api/arduino/monitoreo

## � Características Principales

### 📡 **Sistema de Conectividad Inteligente**
- ✅ **Portal de configuración WiFi automático**
- ✅ **Monitoreo continuo de conectividad a internet** (cada 30 segundos)
- ✅ **Auto-recuperación** ante fallos de conexión
- ✅ **Detección inteligente** de problemas de red
- ✅ **Interfaz web moderna** con funcionalidad mostrar/ocultar contraseña

### 🌡️ **Sensores Integrados**
- ✅ **Sensor de temperatura Dallas DS18B20** (GPIO 4)
- ✅ **Sensor de frecuencia cardíaca MAX30105** (I2C)
- ✅ **Calibración automática** y filtrado de señales
- ✅ **Promedio móvil** para lecturas estables

### 📊 **Transmisión de Datos**
- ✅ **Envío automático cada 10 segundos**
- ✅ **Formato JSON** estructurado
- ✅ **Protocolo HTTPS** seguro
- ✅ **Identificación única** por MAC address

### 🔧 **Control Manual**
- ✅ **Botón de reconfiguración** (GPIO 0 - BOOT)
- ✅ **Activación manual del portal** (mantener presionado 3 segundos)
- ✅ **Diagnóstico por monitor serial**

## � Funcionamiento del Sistema

### � **Ciclo de Operación Normal**
```
[Inicio] → [Conectar WiFi] → [Verificar Internet] → [Inicializar Sensores] → [Loop Principal]
    ↓
[Leer Sensores] → [Enviar Datos] → [Monitorear Conectividad] → [Repetir cada 10s]
```

### 🌐 **Portal de Configuración Automático**

#### **Se Activa Automáticamente En:**
1. **Primera instalación** (sin credenciales WiFi guardadas)
2. **WiFi no disponible** (red fuera de alcance o contraseña incorrecta)
3. **Sin acceso a internet** (después de 3 fallos consecutivos)
4. **Activación manual** (botón BOOT presionado 3 segundos)

#### **Escenarios de Activación:**
```
📊 Scenario 1: Router sin Internet
[✅ WiFi Conectado] → [❌ Sin Internet] → [🔄 3 Reintentos] → [🌐 Portal Activo]

📊 Scenario 2: Contraseña Incorrecta  
[❌ WiFi Rechazado] → [🌐 Portal Inmediato]

📊 Scenario 3: Problema Temporal
[❌ Sin Internet] → [🔄 Verificación] → [✅ Restaurado] → [▶️ Continúa]
```

## � Guía de Uso del Portal

### **�🔧 Primera Configuración**
1. **Flashea el código** en tu ESP32
2. El collar creará automáticamente: **`CollarSalome_Config`**
3. **Conéctate** desde tu dispositivo móvil/computadora
   - 🔑 **Contraseña**: `12345678`
4. **Abre cualquier navegador** y ve a cualquier página
5. **Serás redirigido** automáticamente al portal
6. **Selecciona tu red WiFi** de la lista disponible
7. **Ingresa la contraseña** (usa el botón 👁️ para mostrarla)
8. **Clic en "Guardar y Conectar"**
9. **El collar se reinicia** y se conecta automáticamente

### **🔄 Reconfiguración**
- **Método 1**: Mantén presionado el botón BOOT por 3 segundos
- **Método 2**: El portal se abre automáticamente si hay problemas de conectividad
- **Método 3**: Si no puede conectarse, inicia el portal automáticamente

## 🔧 Especificaciones Técnicas

### **🖥️ Hardware Requerido**
```
• ESP32 (cualquier modelo)
• Sensor Dallas DS18B20 (temperatura)
• Sensor MAX30105 (frecuencia cardíaca)  
• Resistencia pull-up 4.7kΩ (para DS18B20)
• Cables de conexión
• Fuente de alimentación
```

### **📐 Conexiones**
```
DS18B20:
• VCC → 3.3V
• GND → GND  
• DATA → GPIO 4 (con resistencia pull-up a 3.3V)

MAX30105:
• VCC → 3.3V
• GND → GND
• SDA → GPIO 21
• SCL → GPIO 22

Botón de Configuración:
• GPIO 0 (BOOT) → GND (con pull-up interno)
```

### **📚 Librerías Requeridas**
```arduino
// Librerías del ESP32 (incluidas)
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <HTTPClient.h>

// Librerías externas (instalar desde Library Manager)
#include <OneWire.h>           // Para DS18B20
#include <DallasTemperature.h> // Para DS18B20
#include <ArduinoJson.h>       // Para formato JSON
#include "MAX30105.h"          // Para sensor de frecuencia cardíaca
#include "heartRate.h"         // Algoritmo de detección de latidos
```

## ⚙️ Configuración y Personalización

### **🔧 Parámetros Modificables**
```cpp
// En tic_vaca.ino
const String COLLAR_UNO = "2";                    // ID del collar
const String nombre_vaca = "Salome";               // Nombre de la vaca
const unsigned long printPeriod = 10000;          // Intervalo de envío (10s)

// En WiFiConnection.cpp
const char* ap_ssid = "CollarSalome_Config";       // Nombre del portal WiFi
const char* ap_password = "12345678";              // Contraseña del portal
const unsigned long internetCheckInterval = 30000; // Verificación internet (30s)
const int maxConsecutiveFailures = 3;             // Fallos antes del portal

// En DataSender.cpp
const char* serverUrl = "https://pmonitunl.vercel.app/api/arduino/monitoreo";
```

### **📊 Formato de Datos Enviados**
```json
{
  "collar_id": "2",
  "temperatura": 38.5,
  "nombre_vaca": "Salome", 
  "pulsaciones": 72,
  "mac_collar": "AA:BB:CC:DD:EE:FF"
}
```

## 🌐 Características del Portal Web

### **✨ Interfaz Moderna**
- 🎨 **Diseño responsive** para móviles y tablets
- 🔍 **Escaneo automático** de redes WiFi disponibles
- 📶 **Indicadores visuales** de intensidad de señal
- 🔒 **Iconos de seguridad** (redes abiertas/protegidas)
- 👁️ **Botón mostrar/ocultar contraseña**
- ☑️ **Checkbox alternativo** para mostrar contraseña

### **🔍 Información Diagnóstica**
- ⚠️ **Alertas automáticas** sobre problemas detectados
- 💡 **Consejos** para solucionar problemas comunes
- 📋 **Lista detallada** de posibles causas
- 🔄 **Estado en tiempo real** del sistema

### **🛠️ Funcionalidades Avanzadas**
- 🌐 **Captive portal** (redirección automática)
- 🔄 **Auto-refresh** después de configuración
- 📱 **Compatible** con todos los navegadores
- 🚀 **Carga rápida** sin dependencias externas

## 🔒 Seguridad y Confiabilidad

### **🛡️ Medidas de Seguridad**
- 🔐 **Contraseña protegida** para el portal de configuración
- 💾 **Almacenamiento seguro** de credenciales en flash
- 🕒 **Timeout automático** en conexiones fallidas
- 🔄 **Recuperación automática** ante errores

### **📈 Confiabilidad del Sistema**
- 🔄 **Reconexión automática** ante desconexiones
- 📊 **Monitoreo continuo** de conectividad
- 🚨 **Detección proactiva** de problemas
- 📝 **Logging detallado** para diagnóstico

## 🐛 Solución de Problemas

### **❌ Problemas Comunes**

#### **Portal no aparece:**
```
✅ Verificar conexión a "CollarSalome_Config"
✅ Intentar ir directamente a 192.168.4.1
✅ Asegurar que el DNS no esté personalizado
✅ Probar con diferentes navegadores
```

#### **No se conecta al WiFi:**
```
✅ Verificar contraseña (usar botón 👁️)
✅ Confirmar que sea red 2.4GHz (no 5GHz)
✅ Verificar intensidad de señal suficiente
✅ Comprobar que la red tenga acceso a internet
```

#### **Sensores no funcionan:**
```
✅ Revisar conexiones físicas
✅ Verificar alimentación de sensores
✅ Comprobar resistencia pull-up (DS18B20)
✅ Verificar direcciones I2C (MAX30105)
```

#### **No envía datos al servidor:**
```
✅ Verificar conectividad a internet
✅ Comprobar URL del servidor
✅ Revisar formato JSON en monitor serial
✅ Verificar respuesta del servidor
```

### **📋 Monitor Serial - Mensajes Importantes**
```
✅ "Sistema iniciado correctamente" - Todo funcionando
⚠️ "Fallo de internet #X de 3" - Problemas de conectividad
🚨 "Portal de configuración activo" - Necesita reconfiguración
🔄 "Conectividad restaurada" - Problema resuelto automáticamente
```

## 🔄 Actualizaciones Futuras

### **🚀 Características Planificadas**
- 📊 **Dashboard web** integrado en el portal
- ⏰ **Configuración de intervalos** desde la interfaz
- 📱 **Notificaciones push** para eventos críticos
- 🌡️ **Alertas de temperatura** configurables
- 💓 **Monitoreo de salud** avanzado
- 📈 **Gráficos en tiempo real** de los sensores
- 🔋 **Monitoreo de batería** y eficiencia energética

### **🔧 Mejoras Técnicas Pendientes**
- 🛡️ **Autenticación WPA2-Enterprise**
- 🌐 **Soporte para múltiples servidores**
- 📦 **OTA (Over-The-Air) updates**
- 🗄️ **Almacenamiento local** de datos de respaldo

## 📞 Soporte y Mantenimiento

### **📊 Información del Sistema**
- **Versión**: 2.0
- **Fecha**: Septiembre 2025
- **Compatibilidad**: ESP32 (todos los modelos)
- **Protocolo**: HTTP/HTTPS
- **Formato**: JSON

### **🔧 Mantenimiento Recomendado**
- 🔄 **Verificación mensual** de conectividad
- 🧹 **Limpieza de sensores** según ambiente
- 🔋 **Monitoreo de alimentación** continuo
- 📊 **Revisión de logs** periódica

---

**🐄 Desarrollado para el monitoreo eficiente y confiable del ganado**  
*Sistema autónomo con capacidades de auto-diagnóstico y recuperación automática*

## 🔒 Seguridad

- El portal solo se activa cuando es necesario
- Las credenciales se almacenan de forma segura en la memoria flash
- El punto de acceso tiene contraseña por defecto
- Timeout automático si no se puede conectar

## 🐛 Solución de Problemas

### El portal no aparece:
- Verifica que te conectaste a la red `CollarVaca_Config`
- Intenta ir directamente a `192.168.4.1`
- Asegúrate de que tu dispositivo no esté usando DNS personalizado

### No se conecta a mi WiFi:
- Verifica que la contraseña sea correcta
- Asegúrate de que la red esté en 2.4GHz (ESP32 no soporta 5GHz)
- Revisa que la señal WiFi sea suficientemente fuerte

### El dispositivo se reinicia constantemente:
- Verifica las conexiones de los sensores
- Revisa el monitor serial para mensajes de error
- Asegúrate de que las librerías estén instaladas correctamente

## 📊 Funcionamiento Normal

Una vez configurado correctamente:
1. El dispositivo se conecta automáticamente a la red WiFi configurada
2. Lee los sensores de temperatura y ritmo cardíaco
3. Envía los datos al servidor cada 10 segundos
4. Muestra información en el monitor serial

## 🔄 Actualizaciones Futuras Posibles

- Configuración de intervalo de envío de datos desde el portal
- Configuración del nombre de la vaca desde el portal  
- Visualización de datos en tiempo real en el portal
- Modo de diagnóstico con información de sensores
