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
          monitoringMessage1 = 'Resultados en $countdown';
          textColor1 = Colors.black;
        } else {
          isMonitoring2 = true;
          monitoringMessage2 = 'Resultados en $countdown';
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
      final username = Provider.of<UserProvider>(context, listen: false).user?.nombres ?? '';
      print('Usuario: $username');

      _updateMonitoringMessage(sensorNumber, collarId, nombreVaca, temperatura, pulsaciones, registrado);
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
              ),
              SizedBox(height: 20),
              MonitoringButton(
                isMonitoring: isMonitoring1,
                label: 'Collar 1',
                onPressed: () => startMonitoringSensor1(context),
              ),
              SizedBox(height: 20),
              MonitoringCard(
                textColor: textColor2,
                monitoringMessage: monitoringMessage2,
              ),
              SizedBox(height: 20),
              MonitoringButton(
                isMonitoring: isMonitoring2,
                label: 'Collar 2',
                onPressed: () => startMonitoringSensor2(context),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
