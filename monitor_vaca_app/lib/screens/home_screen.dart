import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:monitor_vaca/components/monitoring_card.dart';
import 'package:monitor_vaca/components/monitoring_button.dart';
import 'package:monitor_vaca/services/api_service.dart';
// import 'package:fluttertoast/fluttertoast.dart';  // Comentado por compatibilidad
import 'package:monitor_vaca/utils/providerUser.dart';
import 'package:provider/provider.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool isMonitoring1 = false;
  bool isMonitoring2 = false;
  String monitoringMessage1 = 'Collar 1: Sin monitorear';
  String monitoringMessage2 = 'Collar 2: Sin monitorear';
  Color textColor1 = Colors.black;
  Color textColor2 = Colors.black;
  
  // Rastrear turno registrado
  String? turnoRegistrado1;
  String? turnoRegistrado2;
  
  // Rastrear si está deshabilitado
  bool buttonDisabled1 = false;
  bool buttonDisabled2 = false;

  void startMonitoringSensor1(BuildContext context) async {
    await startMonitoring(context, 1);
  }

  void startMonitoringSensor2(BuildContext context) async {
    await startMonitoring(context, 2);
  }

  Future<void> startMonitoring(BuildContext context, int sensorNumber) async {
    int countdown = 59;
    Timer timer;

    void updateState() {
      setState(() {
        if (sensorNumber == 1) {
          isMonitoring1 = true;
          monitoringMessage1 = 'Resultados en $countdown segundos';
          textColor1 = Colors.black;
        } else {
          isMonitoring2 = true;
          monitoringMessage2 = 'Resultados en $countdown segundos';
          textColor2 = Colors.black;
        }
      });
    }

    updateState();

    timer = Timer.periodic(Duration(seconds: 1), (Timer t) {
      if (countdown > 0) {
        countdown--;
        updateState();
      } else {
        t.cancel();
        fetchData(sensorNumber, context);
      }
    });
  }

  Future<void> fetchData(int sensorNumber, BuildContext context) async {
    try {
      final result = await ApiService.fetchData(context, sensorNumber);
      print('Resultados: $result');
      final datos = result?['datos'];
      print('Datos: $datos');
      final collarId = datos?['collar_id'] ?? 0;
      print('Collar ID: $collarId');
      
      // Extraer valores del último_registro
      final ultimoRegistro = datos?['ultimo_registro'];
      final pulsaciones = ultimoRegistro?['pulsaciones'] ?? 0;
      print('Pulsaciones: $pulsaciones');
      final temperatura = (ultimoRegistro?['temperatura'] ?? 0.0).toDouble();
      print('Temperatura: $temperatura');
      
      final nombreVaca = datos?['nombre'] ?? '';
      print('Nombre de la vaca: $nombreVaca');
      final registrado = datos?['registrado'] ?? false;
      print('Registrado: $registrado');
      final username = Provider.of<UserProvider>(context, listen: false).user?.email ?? '';
      print('Email de usuario: $username');

      _updateMonitoringMessage(sensorNumber, collarId, nombreVaca, temperatura, pulsaciones, registrado);
      
      // Obtener fecha, hora y estado de salud del registro
      final fechaRegistro = ultimoRegistro?['fecha'] ?? '';
      final estadoSalud = ultimoRegistro?['estado_salud'] ?? 'Desconocido';
      
      // Verificar si ya existe lectura en el turno actual
      try {
        final verificacion = await ApiService.verificarLecturaTurno(collarId);
        final lecturaBloqueada = verificacion?['lectura_registrada'] ?? false;
        final turnoDisplay = verificacion?['turno_display'] ?? '';
        
        print('📋 Lectura bloqueada: $lecturaBloqueada');
        
        // Si ya existe lectura en el turno, bloquear directamente
        if (lecturaBloqueada) {
          setState(() {
            if (sensorNumber == 1) {
              buttonDisabled1 = true;
              turnoRegistrado1 = turnoDisplay;
              monitoringMessage1 = 'Collar 1: Datos guardados ($turnoDisplay)';
              textColor1 = Colors.green;
            } else {
              buttonDisabled2 = true;
              turnoRegistrado2 = turnoDisplay;
              monitoringMessage2 = 'Collar 2: Datos guardados ($turnoDisplay)';
              textColor2 = Colors.green;
            }
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('ℹ️ Ya registrado en turno $turnoDisplay'),
              backgroundColor: Colors.blue,
              duration: Duration(seconds: 2),
            ),
          );
          return;
        }
      } catch (e) {
        print('⚠️ Error al verificar lectura: $e');
        // Continuar incluso si falla la verificación
      }
      
      // Obtener ID de la lectura
      final lecturaId = ultimoRegistro?['id'] ?? 0;
      print('Lectura ID: $lecturaId');
      
      // Mostrar modal de confirmación para guardar
      final resultado = await mostrarModalGuardarLectura(
        context: context,
        username: username,
        collarId: collarId,
        lecturaId: lecturaId,
        temperature: temperatura.toInt(),
        heartRate: pulsaciones,
        nombreVaca: nombreVaca,
        fechaRegistro: fechaRegistro,
        estadoSalud: estadoSalud,
        sensorNumber: sensorNumber,
      );

      // Si eligió reintentar, reiniciar el contador
      if (resultado == false) {
        setState(() {
          if (sensorNumber == 1) {
            isMonitoring1 = false;
            monitoringMessage1 = 'Collar 1: Sin monitorear';
            textColor1 = Colors.black;
          } else {
            isMonitoring2 = false;
            monitoringMessage2 = 'Collar 2: Sin monitorear';
            textColor2 = Colors.black;
          }
        });
      }
    } catch (error) {
      print('Error al cargar los datos desde la API: $error');

      _handleFetchError(sensorNumber);
    } finally {
      _setMonitoringState(sensorNumber, false);
    }
  }

  void _updateMonitoringMessage(int sensorNumber, int collarId, String nombreVaca, double temperatura, int pulsaciones, bool registrado) {
    setState(() {
      if (sensorNumber == 1) {
        monitoringMessage1 = 'Collar: $nombreVaca\nTemperatura: $temperatura°C\nPulsaciones: $pulsaciones';
        textColor1 = _getVitalSignColor(pulsaciones, temperatura, 40, 80, 37.0, 39.0);
      } else {
        monitoringMessage2 = 'Collar $collarId: $nombreVaca\nTemperatura: $temperatura°C\nPulsaciones: $pulsaciones';
        textColor2 = _getVitalSignColor(pulsaciones, temperatura, 60, 80, 37.0, 38.0);
      }

      _showToast(registrado);
    });
  }

  Color _getVitalSignColor(int pulsaciones, double temperatura, int minPulse, int maxPulse, double minTemp, double maxTemp) {
    if (pulsaciones >= minPulse && pulsaciones <= maxPulse && temperatura >= minTemp && temperatura <= maxTemp) {
      return Colors.green;
    } else {
      return Colors.red;
    }
  }

  void _handleFetchError(int sensorNumber) {
    setState(() {
      if (sensorNumber == 1) {
        monitoringMessage1 = 'Collar 1: Error al cargar los datos desde la API';
        textColor1 = Colors.red;
      } else {
        monitoringMessage2 = 'Collar 2: Error al cargar los datos desde la API';
        textColor2 = Colors.red;
      }
    });
  }

  void _setMonitoringState(int sensorNumber, bool isMonitoring) {
    setState(() {
      if (sensorNumber == 1) {
        isMonitoring1 = isMonitoring;
      } else {
        isMonitoring2 = isMonitoring;
      }
    });
  }

  void _showToast(bool registrado) {
    String message = registrado ? 'Control registrado' : 'Datos del último registro';
    // Toast no soportado en Windows/Linux - solo mostrar en iOS/Android
    if (Platform.isIOS || Platform.isAndroid) {
      // Fluttertoast.showToast(
      //   msg: message,
      //   toastLength: Toast.LENGTH_LONG,
      //   gravity: ToastGravity.BOTTOM,
      //   timeInSecForIosWeb: 1,
      //   backgroundColor: registrado ? Colors.green : Colors.blue,
      //   textColor: Colors.white,
      //   fontSize: 16.0,
      // );
      print(message);  // Usar print temporalmente
    }
  }

  Future<bool> mostrarModalGuardarLectura({
    required BuildContext context,
    required String username,
    required int collarId,
    required int lecturaId,
    required int temperature,
    required int heartRate,
    required String nombreVaca,
    required int sensorNumber,
    String? observaciones,
    String? fechaRegistro,
    String? estadoSalud,
  }) async {
    // Procesar fecha y hora
    String fecha = '';
    String hora = '';
    String horario = '';
    
    if (fechaRegistro != null && fechaRegistro.isNotEmpty) {
      try {
        // Formato esperado: "2026-01-31 14:29:06.562921"
        final partes = fechaRegistro.split(' ');
        fecha = partes[0]; // "2026-01-31"
        
        if (partes.length > 1) {
          final horaParts = partes[1].split(':');
          final horaInt = int.parse(horaParts[0]);
          hora = '${horaParts[0]}:${horaParts[1]}'; // "14:29"
          
          // Determinar si es AM o PM
          if (horaInt >= 7 && horaInt < 12) {
            horario = 'Mañana';
          } else if (horaInt >= 12 && horaInt < 18) {
            horario = 'Tarde';
          } else if (horaInt >= 18 && horaInt < 24) {
            horario = 'Noche';
          } else {
            horario = 'Madrugada';
          }
        }
      } catch (e) {
        print('Error al procesar fecha: $e');
      }
    }
    
    final resultado = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Text('DATOS CAPTURADOS'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailRow('Id Collar:', collarId.toString()),
              _buildDetailRow('Nombre Bovino:', nombreVaca),
              _buildDetailRow('Temperatura:', '$temperature°'),
              _buildDetailRow('Pulsaciones:', heartRate.toString()),
              _buildDetailRow('Usuario:', username),
              if (fecha.isNotEmpty)
                _buildDetailRow('Fecha:', fecha),
              if (hora.isNotEmpty)
                _buildDetailRow('Hora:', hora),
              if (horario.isNotEmpty)
                _buildDetailRow('Horario:', horario),
              if (estadoSalud != null && estadoSalud.isNotEmpty)
                Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: _buildEstadoSalud(estadoSalud),
                ),
              SizedBox(height: 16),
              Text(
                '¿Desea guardar la Lectura?',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text('Reintentar'),
            onPressed: () => Navigator.of(context).pop(false),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
            ),
            child: Text('Sí, guardar'),
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );

    if (resultado == true) {
      // El usuario confirmó - registrar el control
      try {
        final exito = await ApiService.registrarControl(
          email: username,
          collarId: collarId,
          lecturaId: lecturaId,
          observaciones: observaciones,
        );

        if (exito) {
          // Extraer turno actual
          String turnoActual = _extraerTurno(horario);
          
          // Deshabilitar botón y guardar turno
          setState(() {
            if (sensorNumber == 1) {
              buttonDisabled1 = true;
              turnoRegistrado1 = turnoActual;
              monitoringMessage1 = 'Collar 1: Datos guardados ($turnoActual)';
              textColor1 = Colors.green;
            } else {
              buttonDisabled2 = true;
              turnoRegistrado2 = turnoActual;
              monitoringMessage2 = 'Collar 2: Datos guardados ($turnoActual)';
              textColor2 = Colors.green;
            }
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('✅ Control registrado exitosamente'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );
          
          return true;
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: $e'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 3),
          ),
        );
        return false;
      }
    }
    
    // El usuario eligió "Reintentar" o cerró el diálogo
    return false;
  }

  String _extraerTurno(String horario) {
    // Convertir "Mañana", "Tarde", etc. a formato corto
    if (horario.contains('Mañana')) return 'Mañana';
    if (horario.contains('Tarde')) return 'Tarde';
    if (horario.contains('Noche')) return 'Noche';
    if (horario.contains('Madrugada')) return 'Madrugada';
    return 'Desconocido';
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(value),
        ],
      ),
    );
  }

  Widget _buildEstadoSalud(String estado) {
    Color backgroundColor;
    Color textColor = Colors.white;
    String iconEmoji;

    if (estado.toLowerCase().contains('normal')) {
      backgroundColor = Colors.green;
      iconEmoji = '●'; // Punto verde
    } else if (estado.toLowerCase().contains('alerta')) {
      backgroundColor = Colors.amber;
      iconEmoji = '●'; // Punto amarillo
      textColor = Colors.black;
    } else if (estado.toLowerCase().contains('crítico')) {
      backgroundColor = Colors.red;
      iconEmoji = '●'; // Punto rojo
    } else {
      backgroundColor = Colors.grey;
      iconEmoji = '?';
    }

    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            'Estado: ',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
          Text(
            estado,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: textColor,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        Navigator.of(context).popUntil((route) => route.isFirst);
        return true;
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          title: Row(
            children: [
              Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: Image.asset(
                  'assets/logoCarrera.jpeg',
                  height: 50,
                  width: 50,
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Universidad Nacional de Loja',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                  Text(
                    'Panel de Monitoreo',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                ],
              ),
            ],
          ),
          actions: [
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconTheme(
                  data: IconThemeData(
                    size: 40,
                    shadows: [
                      Shadow(
                        blurRadius: 10.0,
                        color: Colors.black,
                        offset: Offset(2.0, 1.0),
                      ),
                    ],
                    color: const Color.fromRGBO(2, 68, 124, 1),
                  ),
                  child: IconButton(
                    icon: Icon(Icons.logout),
                    onPressed: () {
                      Navigator.of(context).pushNamedAndRemoveUntil(
                        '/login',
                        (Route<dynamic> route) => false,
                      );
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              MonitoringCard(
                textColor: textColor1,
                monitoringMessage: monitoringMessage1,
                turno: turnoRegistrado1,
              ),
              SizedBox(height: 20),
              MonitoringButton(
                isMonitoring: isMonitoring1,
                isDisabled: buttonDisabled1,
                label: 'Collar 1',
                onPressed: () => startMonitoringSensor1(context),
              ),
              SizedBox(height: 20),
              MonitoringCard(
                textColor: textColor2,
                monitoringMessage: monitoringMessage2,
                turno: turnoRegistrado2,
              ),
              SizedBox(height: 20),
              MonitoringButton(
                isMonitoring: isMonitoring2,
                isDisabled: buttonDisabled2,
                label: 'Collar 2',
                onPressed: () => startMonitoringSensor2(context),
              ),
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _refrescarDatos,
          tooltip: 'Actualizar datos',
          backgroundColor: Colors.green,
          child: Icon(Icons.refresh),
        ),
      ),
    );
  }

  void _refrescarDatos() {
    print('🔄 Refrescando datos...');
    
    // Resetear el estado local
    setState(() {
      buttonDisabled1 = false;
      buttonDisabled2 = false;
      turnoRegistrado1 = null;
      turnoRegistrado2 = null;
      isMonitoring1 = false;
      isMonitoring2 = false;
      monitoringMessage1 = 'Collar 1: Sin monitorear';
      monitoringMessage2 = 'Collar 2: Sin monitorear';
      textColor1 = Colors.black;
      textColor2 = Colors.black;
    });
    
    // Traer datos actualizados de los collares
    Future.wait([
      _verificarYActualizarCollar(1),
      _verificarYActualizarCollar(2),
    ]).then((_) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Panel actualizado'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 1),
        ),
      );
    }).catchError((e) {
      print('Error al actualizar: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('⚠️ Error al actualizar'),
          backgroundColor: Colors.orange,
          duration: Duration(seconds: 1),
        ),
      );
    });
  }

  Future<void> _verificarYActualizarCollar(int sensorNumber) async {
    try {
      // Obtener datos del collar
      final result = await ApiService.fetchData(context, sensorNumber);
      final datos = result?['datos'];
      final collarId = datos?['collar_id'] ?? 0;
      final nombreVaca = datos?['nombre'] ?? '';
      final ultimoRegistro = datos?['ultimo_registro'];
      final temperatura = (ultimoRegistro?['temperatura'] ?? 0.0).toDouble();
      final pulsaciones = ultimoRegistro?['pulsaciones'] ?? 0;

      // Verificar si ya existe lectura en el turno actual
      try {
        final verificacion = await ApiService.verificarLecturaTurno(collarId);
        final lecturaBloqueada = verificacion?['lectura_registrada'] ?? false;
        final turnoDisplay = verificacion?['turno_display'] ?? '';
        
        // Obtener datos del registro del API
        final tempAPI = verificacion?['temperatura'];
        final pulsacionesAPI = verificacion?['pulsaciones'];
        final nombreVacaAPI = verificacion?['bovino_nombre'];
        final estadoSalud = verificacion?['estado_salud'] ?? 'Desconocido';

        print('🔍 Verificación - Collar $sensorNumber: bloqueado=$lecturaBloqueada');

        // Usar datos del API si están disponibles, sino usar los obtenidos de fetchData
        final tempFinal = tempAPI ?? temperatura;
        final pulsosFinal = pulsacionesAPI ?? pulsaciones;
        final nombreFinal = nombreVacaAPI ?? nombreVaca;

        // Si ya existe lectura, bloquear
        if (lecturaBloqueada) {
          setState(() {
            if (sensorNumber == 1) {
              buttonDisabled1 = true;
              turnoRegistrado1 = turnoDisplay;
              monitoringMessage1 = 'Collar 1: Datos guardados ($turnoDisplay)';
              textColor1 = Colors.green;
              // Actualizar datos del card
              _updateMonitoringMessage(sensorNumber, collarId, nombreFinal, tempFinal.toDouble(), pulsosFinal, false);
            } else {
              buttonDisabled2 = true;
              turnoRegistrado2 = turnoDisplay;
              monitoringMessage2 = 'Collar 2: Datos guardados ($turnoDisplay)';
              textColor2 = Colors.green;
              // Actualizar datos del card
              _updateMonitoringMessage(sensorNumber, collarId, nombreFinal, tempFinal.toDouble(), pulsosFinal, false);
            }
          });
        } else {
          // Si NO hay lectura, mostrar "Sin Monitorear"
          setState(() {
            if (sensorNumber == 1) {
              buttonDisabled1 = false;
              turnoRegistrado1 = turnoDisplay;
              monitoringMessage1 = 'Collar 1: Sin Monitorear';
              textColor1 = Colors.black;
            } else {
              buttonDisabled2 = false;
              turnoRegistrado2 = turnoDisplay;
              monitoringMessage2 = 'Collar 2: Sin Monitorear';
              textColor2 = Colors.black;
            }
          });
        }
      } catch (e) {
        print('⚠️ Error verificando lectura del collar $sensorNumber: $e');
      }
    } catch (e) {
      print('❌ Error obteniendo datos del collar $sensorNumber: $e');
    }
  }
}
