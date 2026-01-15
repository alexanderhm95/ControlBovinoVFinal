import 'package:flutter/material.dart';

class MonitoringState {
  String monitoringMessage1 = '';
  String monitoringMessage2 = '';
  Color textColor1 = Colors.black;
  Color textColor2 = Colors.black;
  bool isMonitoring1 = false;
  bool isMonitoring2 = false;

  void updateMonitoringState(int sensorNumber, String message, Color color) {
    if (sensorNumber == 1) {
      monitoringMessage1 = message;
      textColor1 = color;
    } else {
      monitoringMessage2 = message;
      textColor2 = color;
    }
  }

  void setMonitoringStatus(int sensorNumber, bool status) {
    if (sensorNumber == 1) {
      isMonitoring1 = status;
    } else {
      isMonitoring2 = status;
    }
  }

  void handleFetchError(int sensorNumber) {
    if (sensorNumber == 1) {
      monitoringMessage1 = 'Collar 1: Error al cargar los datos desde la API';
      textColor1 = Colors.red;
    } else {
      monitoringMessage2 = 'Collar 2: Error al cargar los datos desde la API';
      textColor2 = Colors.red;
    }
  }
}
