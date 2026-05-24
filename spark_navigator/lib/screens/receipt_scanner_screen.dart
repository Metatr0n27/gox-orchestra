import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../widgets/order_heatmap_widget.dart';

class ReceiptScannerScreen extends StatefulWidget {
  @override
  _ReceiptScannerScreenState createState() => _ReceiptScannerScreenState();
}

class _ReceiptScannerScreenState extends State<ReceiptScannerScreen> {
  CameraController? _controller;
  TextEditingController _itemCountController = TextEditingController(text: '1');
  List<Map<String, dynamic>> scannedOrders = [];
  bool _isProcessing = false;
  int _matchedItems = 0;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _loadSavedOrders();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    final backCamera = cameras.firstWhere(
      (cam) => cam.lensDirection == CameraLensDirection.back,
      orElse: () => cameras.first,
    );

    _controller = CameraController(backCamera, ResolutionPreset.high);
    await _controller!.initialize();
    setState(() {});
  }

  Future<void> _loadSavedOrders() async {
    final box = Hive.box('orders');
    setState(() {
      scannedOrders = box.values.map((e) => Map<String, dynamic>.from(e)).toList();
    });
  }

  Future<void> _scanAndMatch() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    
    setState(() => _isProcessing = true);

    try {
      final image = await _controller!.takePicture();
      final inputFile = InputImage.fromFilePath(image.path);
      
      final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
      final recognizedText = await recognizer.processImage(inputFile);
      
      // Extract item count from receipt
      final extractedCount = _parseItemCount(recognizedText.text);
      
      await recognizer.close();
      
      final enteredCount = int.tryParse(_itemCountController.text) ?? 1;
      final matchStatus = extractedCount == enteredCount ? 'MATCH' : 'VERIFY';
      
      // Save order
      final orderId = DateTime.now().millisecondsSinceEpoch.toString();
      final box = Hive.box('orders');
      
      await box.put(orderId, {
        'scanned_items': extractedCount,
        'entered_items': enteredCount,
        'match_status': matchStatus,
        'receipt_preview': recognizedText.text.substring(0, 100),
        'photo_path': image.path,
        'created_at': DateTime.now().toIso8601String(),
      });
      
      await _loadSavedOrders();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(matchStatus == 'MATCH' 
              ? '✅ Perfect match! $extractedCount items confirmed.'
              : '⚠️ Verify: Scanner saw $extractedCount, you entered $enteredCount'),
          backgroundColor: matchStatus == 'MATCH' ? Colors.green : Colors.orange,
          duration: Duration(seconds: 3),
        ),
      );
    } catch (e) {
      print('Scan error: $e');
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  int _parseItemCount(String text) {
    // Common receipt patterns
    final patterns = [
      RegExp(r'(\d+)\s*(?:ITEMS?|PCS?|PIECES?)', caseSensitive: false),
      RegExp(r'(?:TOTAL|SUBTOTAL).*?(\d+)', caseSensitive: false),
      RegExp(r'^\s*\d+\.\s+(.+)$', multiLine: true), // Numbered lines
    ];

    for (final regex in patterns) {
      final match = regex.firstMatch(text);
      if (match != null) {
        return int.tryParse(match.group(1) ?? '') ?? 1;
      }
    }

    // Count numbered lines as fallback
    final lines = text.split('\n');
    int count = 0;
    for (final line in lines) {
      if (RegExp(r'^\s*\d+[.)]\s').hasMatch(line)) {
        count++;
      }
    }
    
    return count > 0 ? count : 1;
  }

  @override
  void dispose() {
    _controller?.dispose();
    _itemCountController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Receipt Matcher')),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Camera preview
            AspectRatio(
              aspectRatio: 3 / 4,
              child: _controller != null && _controller!.value.isInitialized
                  ? Stack(
                      alignment: Alignment.center,
                      children: [
                        CameraPreview(_controller!),
                        Positioned(
                          bottom: 20,
                          child: ElevatedButton.icon(
                            onPressed: _isProcessing ? null : _scanAndMatch,
                            icon: _isProcessing
                                ? CircularProgressIndicator(color: Colors.white)
                                : Icon(Icons.camera_alt),
                            label: Text(_isProcessing ? 'SCANNING...' : 'SCAN RECEIPT'),
                            style: ElevatedButton.styleFrom(
                              padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                              backgroundColor: Theme.of(context).primaryColor,
                            ),
                          ),
                        ),
                      ],
                    )
                  : Center(child: CircularProgressIndicator()),
            ),

            Divider(),

            // Manual entry
            Padding(
              padding: EdgeInsets.all(16),
              child: TextField(
                controller: _itemCountController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Enter Expected Item Count',
                  suffixIcon: IconButton(
                    icon: Icon(Icons.add_shopping_cart),
                    onPressed: () {
                      final count = int.tryParse(_itemCountController.text) ?? 1;
                      setState(() {
                        _itemCountController.text = (count + 1).toString();
                      });
                    },
                  ),
                ),
              ),
            ),

            // Saved orders list with heatmap
            ListView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: scannedOrders.length,
              itemBuilder: (ctx, idx) {
                final order = scannedOrders.reversed.toList()[idx];
                final items = order['entered_items'] as int? ?? 1;
                
                return OrderHeatmapWidget(
                  itemCount: items,
                  isCompleted: order['match_status'] == 'MATCH',
                  onTap: () => _showOrderDetail(order),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showOrderDetail(Map<String, dynamic> order) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Order Details'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Expected: ${order['entered_items']} items'),
            Text('Scanned: ${order['scanned_items']} items'),
            Text('Status: ${order['match_status']}'),
            SizedBox(height: 8),
            Text('Date: ${order['created_at']}'.substring(0, 19)),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text('CLOSE'))
        ],
      ),
    );
  }
}
