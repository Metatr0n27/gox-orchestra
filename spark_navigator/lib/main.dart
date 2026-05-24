import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  await Hive.openBox('orders');
  runApp(SparkNavApp());
}

class SparkNavApp extends StatelessWidget {
  @override
  Widget build(BuildContext ctx) => MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: ThemeData(primaryColor: Color(0xFF00AA55), scaffoldBackgroundColor: Color(0xFFF8F8F8)),
    home: HomeScreen(),
  );
}
