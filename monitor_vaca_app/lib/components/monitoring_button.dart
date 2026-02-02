import 'package:flutter/material.dart';

class MonitoringButton extends StatelessWidget {
  final bool isMonitoring;
  final bool isDisabled;
  final String label;
  final VoidCallback onPressed;

  const MonitoringButton({
    required this.isMonitoring,
    this.isDisabled = false,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isDisabled ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: isDisabled ? Colors.grey : Colors.blue,
        padding: EdgeInsets.all(10.0),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10.0),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            isDisabled ? 'Controlado' : 'CAPTURAR',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white,
            ),
          ),
          if (!isDisabled) ...[
            SizedBox(width: 8),
            Icon(
              Icons.camera_alt,
              size: 24,
              color: Colors.white,
            ),
          ] else ...[
            SizedBox(width: 8),
            Icon(
              Icons.storage,
              size: 24,
              color: Colors.white,
            ),
          ]
        ],
      ),
    );
  }
}
