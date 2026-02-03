import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:monitor_vaca/utils/providerUser.dart';
import 'package:monitor_vaca/utils/user.dart';
import 'package:provider/provider.dart';

class ApiService {
  // URL LOCAL para testing: http://127.0.0.1:8000/api
  // URL PRODUCCIÓN: https://pmonitunl.vercel.app/api
  static const String _baseUrl = 'https://pmonitunl.vercel.app/api'; // ← USANDO VERCEL PARA MOBILE
  static String? _authToken;

  // Setter para almacenar token
  static void setAuthToken(String token) {
    _authToken = token;
  }

  // Obtener token almacenado
  static String? getAuthToken() {
    return _authToken;
  }

  // Headers con autenticación
  static Map<String, String> _getHeaders({bool includeAuth = true}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (includeAuth && _authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }

  /// LOGIN - Autentica un usuario y retorna datos de usuario con token
  static Future<User?> login(String username, String password) async {
    try {
      print("🔐 Login iniciado para usuario: $username");
      
      final response = await http.post(
        Uri.parse('$_baseUrl/movil/login/'),
        headers: _getHeaders(includeAuth: false),
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      print("📡 Respuesta login: ${response.statusCode}");

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        
        // Almacenar token si viene en la respuesta
        if (jsonResponse['token'] != null) {
          setAuthToken(jsonResponse['token']);
          print("✅ Token guardado");
        }
        
        return User.fromJson(jsonResponse['data']);
      } else {
        print("❌ Error en login: ${response.statusCode}");
        return null;
      }
    } catch (error) {
      print("❌ Error en login: $error");
      throw error;
    }
  }

  /// OBTENER DATOS - Obtiene datos históricos de un collar por ID
  static Future<Map<String, dynamic>?> fetchData(
      BuildContext context, int collarId) async {
    try {
      print("📊 Obteniendo datos del collar: $collarId");
      
      final response = await http.get(
        Uri.parse('$_baseUrl/movil/datos/$collarId/'),
        headers: _getHeaders(),
      );

      print("📡 Respuesta datos: ${response.statusCode}");

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        
        if (data != null) {
          print("✅ Datos obtenidos correctamente");
          return data;
        } else {
          throw Exception('Datos inválidos o no encontrados');
        }
      } else if (response.statusCode == 401) {
        print("❌ No autorizado - Token expirado");
        _authToken = null;
        throw Exception('Sesión expirada. Por favor, inicia sesión nuevamente');
      } else {
        throw Exception('Error al cargar los datos: ${response.statusCode}');
      }
    } catch (error) {
      print("❌ Error en fetchData: $error");
      throw error;
    }
  }

  /// VERIFICAR LECTURA - Verifica si ya existe lectura registrada en el turno actual
  static Future<Map<String, dynamic>?> verificarLecturaTurno(int collarId) async {
    try {
      print("🔍 Verificando lectura del turno para collar: $collarId");
      
      final response = await http.get(
        Uri.parse('$_baseUrl/movil/verificar-lectura/$collarId/'),
        headers: _getHeaders(),
      );

      print("📡 Respuesta verificación: ${response.statusCode}");

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        
        if (data != null) {
          print("✅ Datos de verificación obtenidos");
          print("   - Lectura registrada: ${data['lectura_registrada']}");
          print("   - Turno: ${data['turno_display']}");
          return data;
        } else {
          throw Exception('Datos de verificación inválidos');
        }
      } else if (response.statusCode == 404) {
        print("ℹ️ Collar no encontrado o sin datos");
        // Retornar estado vacío para collares sin datos
        return {
          'collar_id': collarId,
          'lectura_registrada': false,
          'bloqueado': false,
          'mensaje': 'Collar sin monitorear'
        };
      } else if (response.statusCode == 401) {
        print("❌ No autorizado");
        _authToken = null;
        throw Exception('Sesión expirada');
      } else {
        throw Exception('Error al verificar: ${response.statusCode}');
      }
    } catch (error) {
      print("❌ Error en verificarLecturaTurno: $error");
      throw error;
    }
  }

  /// REGISTRAR CONTROL - Registra un control de monitoreo de una lectura existente
  /// Requiere que la lectura sea del día actual
  static Future<bool> registrarControl({
    required String email,
    required int collarId,
    required int lecturaId,
    String? observaciones,
  }) async {
    try {
      print("📤 Registrando control - Collar: $collarId, Lectura: $lecturaId, Email: $email");
      
      final response = await http.post(
        Uri.parse('$_baseUrl/movil/datos/'),
        headers: _getHeaders(),
        body: jsonEncode({
          'email': email,
          'collar_id': collarId,
          'lectura_id': lecturaId,  // ID de la Lectura existente
          'observaciones': observaciones ?? '',
        }),
      );

      print("📡 Respuesta registro: ${response.statusCode}");

      if (response.statusCode == 201 || response.statusCode == 200) {
        print("✅ Control registrado correctamente");
        var data = json.decode(response.body);
        print("   - Control ID: ${data['control_id']}");
        print("   - Lectura ID: ${data['lectura_id']}");
        return true;
      } else if (response.statusCode == 400) {
        var data = json.decode(response.body);
        print("⚠️ Error de validación: ${data['detalle']}");
        throw Exception(data['detalle'] ?? 'Error al registrar control');
      } else if (response.statusCode == 401) {
        print("❌ No autorizado - Token expirado");
        _authToken = null;
        throw Exception('Sesión expirada');
      } else if (response.statusCode == 404) {
        print("❌ Usuario no encontrado - Verifica el email: $email");
        throw Exception('Usuario no encontrado con email: $email');
      } else {
        print("❌ Error al registrar: ${response.statusCode}");
        var data = json.decode(response.body);
        print("   Detalle: ${data['detalle']}");
        throw Exception(data['detalle'] ?? 'Error desconocido');
      }
    } catch (error) {
      print("❌ Error en registrarControl: $error");
      rethrow;
    }
  }

  /// ENVIAR DATOS - Ahora funciona igual que registrarControl (envía email, collar_id, lectura_id, observaciones)
  /// Útil si necesitas compatibilidad con el backend actual
  static Future<bool> sendSensorData({
    required String email,
    required int collarId,
    required int lecturaId,
    String? observaciones,
  }) async {
    try {
      print("📤 Enviando datos de sensores (modo registrarControl) - Collar: $collarId, Lectura: $lecturaId, Email: $email");
      final response = await http.post(
        Uri.parse('$_baseUrl/movil/datos/'),
        headers: _getHeaders(),
        body: jsonEncode({
          'email': email,
          'username': email,
          'collar_id': collarId,
          'lectura_id': lecturaId,
          'observaciones': observaciones ?? '',
        }),
      );

      print("📡 Respuesta envío: \\${response.statusCode}");

      if (response.statusCode == 201 || response.statusCode == 200) {
        print("✅ Datos enviados correctamente (modo registrarControl)");
        return true;
      } else if (response.statusCode == 401) {
        print("❌ No autorizado - Token expirado");
        _authToken = null;
        throw Exception('Sesión expirada');
      } else if (response.statusCode == 404) {
        print("❌ Usuario no encontrado - Verifica el email");
        throw Exception('Usuario no encontrado con email: $email');
      } else {
        print("❌ Error al enviar datos: \\${response.statusCode}");
        var errorData = json.decode(response.body);
        print("   Detalle: \\${errorData['detalle']}");
        return false;
      }
    } catch (error) {
      print("❌ Error en sendSensorData: $error");
      return false;
    }
  }

  /// OBTENER MONITOREO ACTUAL - Obtiene datos en tiempo real del collar
  static Future<Map<String, dynamic>?> getMonitoreoActual(int collarId) async {
    try {
      print("⏱️ Obteniendo monitoreo actual - Collar: $collarId");
      
      final response = await http.get(
        Uri.parse('$_baseUrl/monitor/datos/$collarId/'),
        headers: _getHeaders(),
      );

      print("📡 Respuesta monitoreo: ${response.statusCode}");

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        print("✅ Monitoreo actual obtenido");
        return data;
      } else if (response.statusCode == 401) {
        _authToken = null;
        throw Exception('Sesión expirada');
      } else {
        throw Exception('Error al obtener monitoreo: ${response.statusCode}');
      }
    } catch (error) {
      print("❌ Error en getMonitoreoActual: $error");
      return null;
    }
  }

  /// OBTENER ÚLTIMO REGISTRO - Obtiene el registro más reciente de un collar
  static Future<Map<String, dynamic>?> getUltimoRegistro(int collarId) async {
    try {
      print("📌 Obteniendo último registro - Collar: $collarId");
      
      final response = await http.get(
        Uri.parse('$_baseUrl/ultimo/registro/$collarId'),
        headers: _getHeaders(),
      );

      print("📡 Respuesta último registro: ${response.statusCode}");

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        print("✅ Último registro obtenido");
        return data;
      } else if (response.statusCode == 404) {
        print("⚠️ No hay registros para este collar");
        return null;
      } else if (response.statusCode == 401) {
        _authToken = null;
        throw Exception('Sesión expirada');
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } catch (error) {
      print("❌ Error en getUltimoRegistro: $error");
      return null;
    }
  }

  /// LOGOUT - Limpia el token local
  static void logout() {
    print("🚪 Cerrando sesión");
    _authToken = null;
    print("✅ Sesión cerrada");
  }

  /// VALIDAR CONEXIÓN - Verifica si el servidor está disponible
  static Future<bool> validateConnection() async {
    try {
      print("🔍 Validando conexión con servidor...");
      
      final response = await http.get(
        Uri.parse('$_baseUrl/movil/login/'),
        headers: _getHeaders(includeAuth: false),
      ).timeout(
        const Duration(seconds: 5),
        onTimeout: () => http.Response('Timeout', 408),
      );

      final isConnected = response.statusCode != 408;
      print(isConnected ? "✅ Servidor disponible" : "❌ Servidor no disponible");
      return isConnected;
    } catch (error) {
      print("❌ Error de conectividad: $error");
      return false;
    }
  }
}
