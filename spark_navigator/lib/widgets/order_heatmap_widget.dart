import 'package:flutter/material.dart';

/// Generates 50 shades of GREEN (items 1-50) then BLUE (items 51-100)
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
  _OrderHeatmapWidgetState createState() => _OrderHeatmapWidgetState();
}

class _OrderHeatmapWidgetState extends State<OrderHeatmapWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  /// Returns heatmap color based on item count
  /// Green gradient: items 1-50 (light to dark)
  /// Blue gradient: items 51-100 (light to dark)
  Color getColorForItemCount(int count) {
    if (count <= 0) return Colors.grey.shade300;
    
    // Clamp to max 100
    final normalizedCount = count.clamp(1, 100);
    
    if (normalizedCount <= 50) {
      // GREEN spectrum (items 1-50)
      final ratio = (normalizedCount - 1) / 49; // 0.0 to 1.0
      return Color.lerp(
        Color(0xFFE8F5E9), // Lightest green
        Color(0xFF1B5E20), // Darkest green
        ratio,
      )!;
    } else {
      // BLUE spectrum (items 51-100)
      final ratio = (normalizedCount - 51) / 49; // 0.0 to 1.0
      return Color.lerp(
        Color(0xFFE3F2FD), // Lightest blue
        Color(0xFF0D47A1), // Darkest blue
        ratio,
      )!;
    }
  }

  String getSpectrumLabel(int count) {
    if (count <= 50) return 'GREEN Zone';
    return 'BLUE Zone';
  }

  IconData getItemIcon(int count) {
    if (count <= 10) return Icons.shopping_bag_outlined;
    if (count <= 25) return Icons.shopping_cart_outlined;
    if (count <= 50) return Icons.local_shipping_outlined;
    if (count <= 75) return Icons.inventory_2_outlined;
    return Icons.warehouse_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final baseColor = getColorForItemCount(widget.itemCount);
    final textColor = widget.itemCount > 25 ? Colors.white : Colors.black87;

    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _pulseAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: widget.isCompleted ? 1.0 : _pulseAnimation.value,
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    baseColor.withOpacity(0.8),
                    baseColor,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: baseColor.withOpacity(0.4),
                    blurRadius: 12,
                    offset: Offset(0, 4),
                  ),
                ],
                border: Border.all(
                  color: widget.isCompleted ? Colors.greenAccent : Colors.transparent,
                  width: 3,
                ),
              ),
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Row(
                  children: [
                    // Item count circle
                    Container(
                      width: 70,
                      height: 70,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            getItemIcon(widget.itemCount),
                            color: textColor,
                            size: 24,
                          ),
                          SizedBox(height: 4),
                          Text(
                            '${widget.itemCount}',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: textColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    SizedBox(width: 20),
                    
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  getSpectrumLabel(widget.itemCount),
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: textColor,
                                  ),
                                ),
                              ),
                              Spacer(),
                              if (widget.isCompleted)
                                Icon(Icons.check_circle, color: Colors.greenAccent, size: 28),
                            ],
                          ),
                          
                          SizedBox(height: 8),
                          
                          Text(
                            widget.itemCount == 1
                                ? 'Single Item Delivery'
                                : '${widget.itemCount} Items in Order',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: textColor,
                            ),
                          ),
                          
                          SizedBox(height: 4),
                          
                          LinearProgressIndicator(
                            value: widget.itemCount / 100,
                            backgroundColor: Colors.white.withOpacity(0.3),
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Colors.white,
                            ),
                            minHeight: 6,
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
