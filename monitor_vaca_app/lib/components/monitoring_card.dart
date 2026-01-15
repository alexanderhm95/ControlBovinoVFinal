import 'package:flutter/material.dart';

class MonitoringCard extends StatelessWidget {
  final Color textColor;
  final String monitoringMessage;

  const MonitoringCard({
    required this.textColor,
    required this.monitoringMessage,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Color.fromARGB(255, 237, 249, 255),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10.0),
      ),
      elevation: 5,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(
              Icons.sensors,
              color: textColor,
              size: 50,
            ),
            //SizedBox(height: 4),
            Text(
              monitoringMessage,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: textColor,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
