import 'package:flutter/material.dart';
import 'package:monitor_vaca/screens/login_screen.dart';
import 'package:monitor_vaca/screens/home_screen.dart';
import 'package:provider/provider.dart';
import 'package:monitor_vaca/utils/providerUser.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => UserProvider()),
      ],
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/login', // Define la ruta inicial
      routes: {
        '/login': (context) => LoginScreen(),
        '/home': (context) => HomeScreen(),
      },
    );
  }
}
