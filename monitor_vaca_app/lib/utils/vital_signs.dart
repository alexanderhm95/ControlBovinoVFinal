import 'package:flutter/material.dart';

class VitalSignsChecker {
  static Color checkVitalSigns(
      int pulsaciones,
      double temperatura,
      int minPulsaciones,
      int maxPulsaciones,
      double minTemperatura,
      double maxTemperatura) {
    if (pulsaciones >= minPulsaciones &&
        pulsaciones <= maxPulsaciones &&
        temperatura >= minTemperatura &&
        temperatura <= maxTemperatura) {
      return Colors.green;
    } else {
      return Colors.red;
    }
  }
}
