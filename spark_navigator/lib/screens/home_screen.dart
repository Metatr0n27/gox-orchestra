import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/order_heatmap_widget.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> todaysOrders = [];
  double totalEarned = 0.0;
  String apiUrl = 'http://10.0.2.2:8765'; // Android emulator host

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    try {
      final resp = await http.get(Uri.parse('$apiUrl/earnings'));
      if (resp.statusCode == 200) {
        final data = json.decode(resp.body);
        setState(() {
          todaysOrders = data['events'] ?? [];
          totalEarned = (data['total'] ?? 0).toDouble();
        });
      }
    } catch (_) {}
  }

  Future<void> _addTestEarning() async {
    await http.post(Uri.parse('$apiUrl/earnings'), headers: {'Content-Type':'application/json'}, body: json.encode({'amount': 8.50, 'source': 'mobile_entry'}));
    _refresh();
  }

  @override
  Widget build(BuildContext ctx) => Scaffold(
    appBar: AppBar(title: Text('Spark Navigator'), actions: [IconButton(icon: Icon(Icons.refresh), onPressed: _refresh)]),
    body: RefreshIndicator(
      onRefresh: _refresh,
      child: todaysOrders.isEmpty
          ? Center(child: Text('No orders logged yet.\nAdd one below.', textAlign: TextAlign.center))
          : ListView.builder(itemCount: todaysOrders.length, itemBuilder: (_, i) {
              final evt = todaysOrders[i];
              return ListTile(
                leading: CircleAvatar(child: Text('\$${evt['amount']}')),
                title: Text(evt['source'] ?? 'Unknown'),
                subtitle: Text(evt['time'].toString().substring(11, 19)),
              );
            }),
    ),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: _addTestEarning,
      icon: Icon(Icons.add),
      label: Text('Log \$8.50'),
      backgroundColor: Color(0xFF00AA55),
    ),
    bottomNavigationBar: BottomAppBar(
      child: Padding(padding: EdgeInsets.all(12), child: Text('Total Today: \$${totalEarned.toStringAsFixed(2)}', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18))),
    ),
  );
}
