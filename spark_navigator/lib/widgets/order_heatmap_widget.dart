import 'package:flutter/material.dart';

class OrderHeatmapWidget extends StatefulWidget {
  final int itemCount;
  final bool isCompleted;
  final VoidCallback? onTap;

  const OrderHeatmapWidget({
    Key? key,
    required this.itemCount,
    this.isCompleted = false,
    this.onTap,
  }) : super(key: key);

  @override
  State<OrderHeatmapWidget> createState() => _OrderHeatmapWidgetState();
}

class _OrderHeatmapWidgetState extends State<OrderHeatmapWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(duration: Duration(milliseconds: 1500), vsync: this)..repeat(reverse: true);
    _pulseAnim = Tween(begin: 1.0, end: 1.08).animate(CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  Color heatColor(int n) {
    if (n <= 0) return Colors.grey.shade300;
    final c = n.clamp(1, 100);
    if (c <= 50) {
      return Color.lerp(const Color(0xFFE8F5E9), const Color(0xFF1B5E20), (c - 1) / 49)!;
    }
    return Color.lerp(const Color(0xFFE3F2FD), const Color(0xFF0D47A1), (c - 51) / 49)!;
  }

  String zoneLabel(int n) => n <= 50 ? 'GREEN Zone' : 'BLUE Zone';

  IconData itemIcon(int n) {
    if (n <= 10) return Icons.shopping_bag_outlined;
    if (n <= 25) return Icons.shopping_cart_outlined;
    if (n <= 50) return Icons.local_shipping_outlined;
    if (n <= 75) return Icons.inventory_2_outlined;
    return Icons.warehouse_outlined;
  }

  @override
  Widget build(BuildContext ctx) {
    final col = heatColor(widget.itemCount);
    final txtCol = widget.itemCount > 25 ? Colors.white : Colors.black87;

    return GestureDetector(
      onTap: widget.onTap,
      child: ScaleTransition(
        scale: widget.isCompleted ? AlwaysStoppedAnimation(1.0) : _pulseAnim,
        child: Container(
          margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [col.withOpacity(.85), col], begin: Alignment.topLeft, end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [BoxShadow(color: col.withOpacity(.35), blurRadius: 12, offset: Offset(0, 4))],
            border: Border.all(color: widget.isCompleted ? Colors.greenAccent : Colors.transparent, width: 3),
          ),
          child: Padding(
            padding: EdgeInsets.all(18),
            child: Row(children: [
              Container(
                width: 66, height: 66,
                decoration: BoxDecoration(color: Colors.white.withOpacity(.2), shape: BoxShape.circle),
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  Icon(itemIcon(widget.itemCount), color: txtCol, size: 22),
                  SizedBox(height: 3),
                  Text('${widget.itemCount}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: txtCol)),
                ]),
              ),
              SizedBox(width: 16),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  Container(padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(color: Colors.white.withOpacity(.2), borderRadius: BorderRadius.circular(10)),
                    child: Text(zoneLabel(widget.itemCount), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: txtCol))),
                  Spacer(),
                  if (widget.isCompleted) Icon(Icons.check_circle, color: Colors.greenAccent, size: 26),
                ]),
                SizedBox(height: 7),
                Text(widget.itemCount == 1 ? 'Single Item' : '${widget.itemCount} Items', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600, color: txtCol)),
                SizedBox(height: 5),
                ClipRRect(borderRadius: BorderRadius.circular(3),
                  child: LinearProgressIndicator(value: widget.itemCount / 100, backgroundColor: Colors.white.withOpacity(.25), valueColor: AlwaysStoppedAnimation(Colors.white), minHeight: 5)),
              ])),
            ]),
          ),
        ),
      ),
    );
  }
}
