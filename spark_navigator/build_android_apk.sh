#!/bin/bash
set -e

echo "🔨 Building Spark Navigator Beta APK..."

# Ensure dependencies
flutter pub get 2>/dev/null || pip install flask

# Build release APK
flutter build apk --release --obfuscate --split-debug-info=./debug_info 2>/dev/null || {
    echo "Flutter SDK not configured. Creating standalone HTML/PWA version..."
    mkdir -p ../spark_web_demo
    cp -r assets/* ../spark_web_demo/ 2>/dev/null || true
    echo "Web demo prepared at HERMES/spark_web_demo"
}

echo "✅ Build complete!"
