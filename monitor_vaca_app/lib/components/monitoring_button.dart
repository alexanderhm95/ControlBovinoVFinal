import 'package:flutter/material.dart';

class MonitoringButton extends StatelessWidget {
  final bool isMonitoring;
  final String label;
  final VoidCallback onPressed;

  const MonitoringButton({
    required this.isMonitoring,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(
        isMonitoring ? Icons.hourglass_empty : Icons.play_arrow,
        size: 30,
      ),
      label: Text(
        isMonitoring ? '$label ' : '$label (desactivado)',
        style: TextStyle(
          fontSize: 16,
          color: Colors.white,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        padding: EdgeInsets.all(10.0),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10.0),
        ),
      ),
    );
  }
}
