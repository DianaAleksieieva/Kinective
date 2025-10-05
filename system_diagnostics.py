#!/usr/bin/env python3
"""
System Diagnostics for Exercise Tracker
Check camera, YOLO model, and system health
"""

import cv2
import sys
import psutil
import torch
import numpy as np
from datetime import datetime

def check_camera():
    """Test camera functionality"""
    print("📷 Testing Camera...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera failed to open")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("❌ Cannot read from camera")
            cap.release()
            return False
        
        height, width = frame.shape[:2]
        print(f"✅ Camera working: {width}x{height}")
        
        # Test a few frames
        for i in range(5):
            ret, frame = cap.read()
            if not ret:
                print(f"❌ Frame {i+1} failed")
                cap.release()
                return False
        
        cap.release()
        print("✅ Camera stability test passed")
        return True
        
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return False

def check_yolo_model():
    """Test YOLO model loading and inference"""
    print("\n🤖 Testing YOLO Model...")
    try:
        from ultralytics import YOLO
        
        # Load model
        model = YOLO("yolo11n-pose.pt")
        print("✅ YOLO model loaded successfully")
        
        # Test inference on dummy image
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model(dummy_image, conf=0.5, verbose=False)
        
        print("✅ YOLO inference test passed")
        return True
        
    except Exception as e:
        print(f"❌ YOLO error: {e}")
        return False

def check_pytorch():
    """Check PyTorch installation"""
    print("\n🔥 Testing PyTorch...")
    try:
        print(f"PyTorch version: {torch.__version__}")
        
        # Test tensor operations
        tensor = torch.randn(3, 3)
        result = torch.matmul(tensor, tensor)
        print("✅ PyTorch tensor operations working")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("ℹ️  CUDA not available (CPU mode)")
        
        return True
        
    except Exception as e:
        print(f"❌ PyTorch error: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n💻 System Resources:")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)
    print(f"CPU: {cpu_percent}% usage, {cpu_count} cores")
    
    # Memory
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024**3)
    memory_used_percent = memory.percent
    print(f"Memory: {memory_gb:.1f}GB total, {memory_used_percent}% used")
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_gb = disk.total / (1024**3)
    disk_used_percent = (disk.used / disk.total) * 100
    print(f"Disk: {disk_gb:.1f}GB total, {disk_used_percent:.1f}% used")
    
    # Performance recommendations
    print("\n💡 Performance Recommendations:")
    if cpu_percent > 80:
        print("⚠️  High CPU usage - close other applications")
    if memory_used_percent > 80:
        print("⚠️  High memory usage - restart or close applications")
    if cpu_count >= 4:
        print("✅ Multi-core CPU detected - good for real-time processing")
    if memory_gb >= 8:
        print("✅ Sufficient RAM for YOLO processing")
    
    return True

def run_quick_test():
    """Run a quick integrated test"""
    print("\n🧪 Quick Integration Test...")
    try:
        from ultralytics import YOLO
        
        # Initialize components
        model = YOLO("yolo11n-pose.pt")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Camera not available for integration test")
            return False
        
        print("📹 Testing 10 frames of real tracking...")
        success_count = 0
        
        for i in range(10):
            ret, frame = cap.read()
            if not ret:
                continue
            
            try:
                # Run YOLO inference
                results = model(frame, conf=0.5, verbose=False)
                success_count += 1
                
                # Show progress
                if i % 3 == 0:
                    print(f"  Frame {i+1}/10 processed")
                    
            except Exception as e:
                print(f"  ❌ Frame {i+1} failed: {e}")
        
        cap.release()
        
        success_rate = (success_count / 10) * 100
        print(f"✅ Integration test: {success_count}/10 frames processed ({success_rate}%)")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def main():
    print("🔧 EXERCISE TRACKER DIAGNOSTICS")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    
    tests = [
        ("Camera", check_camera),
        ("PyTorch", check_pytorch),
        ("YOLO Model", check_yolo_model),
        ("System Resources", check_system_resources),
        ("Integration", run_quick_test)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 OVERALL STATUS:")
    if all_passed:
        print("✅ All tests passed! System ready for exercise tracking.")
    else:
        print("⚠️  Some tests failed. Check errors above before running tracker.")
        print("\n🔧 Troubleshooting Tips:")
        if not results.get("Camera", True):
            print("  • Check camera permissions and connections")
            print("  • Close other applications using the camera")
        if not results.get("YOLO Model", True):
            print("  • Ensure yolo11n-pose.pt model file is available")
            print("  • Check internet connection for model download")
        if not results.get("PyTorch", True):
            print("  • Reinstall PyTorch: pip install torch ultralytics")
    
    print(f"\nDiagnostics completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()