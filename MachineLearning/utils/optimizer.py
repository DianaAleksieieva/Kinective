#!/usr/bin/env python3
"""
Performance Optimization Module
CPU/GPU monitoring, frame rate optimization, and system tuning
"""

import psutil
import time
import cv2
import numpy as np
from threading import Thread
import queue
import json
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class PerformanceMetrics:
    fps: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float]
    inference_time: float
    frame_processing_time: float

class PerformanceOptimizer:
    def __init__(self):
        self.metrics_history = []
        self.optimization_settings = {
            "frame_skip": 1,
            "resolution_scale": 1.0,
            "confidence_threshold": 0.5,
            "detection_interval": 1,
            "enable_threading": True
        }
        self.target_fps = 30
        self.frame_queue = queue.Queue(maxsize=5)
        
    def monitor_system_performance(self) -> PerformanceMetrics:
        """Monitor real-time system performance"""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Try to get GPU usage (if available)
        gpu_usage = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
        except ImportError:
            pass
        
        # Placeholder for timing metrics (to be updated during actual processing)
        metrics = PerformanceMetrics(
            fps=0,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            inference_time=0,
            frame_processing_time=0
        )
        
        return metrics
    
    def adaptive_quality_adjustment(self, current_fps: float, target_fps: float = 30):
        """Automatically adjust quality settings based on performance"""
        fps_ratio = current_fps / target_fps
        
        if fps_ratio < 0.7:  # Performance is poor
            print("⚠️  Performance below target, reducing quality...")
            
            # Increase frame skipping
            if self.optimization_settings["frame_skip"] < 3:
                self.optimization_settings["frame_skip"] += 1
                print(f"  📉 Frame skip increased to {self.optimization_settings['frame_skip']}")
            
            # Reduce resolution
            if self.optimization_settings["resolution_scale"] > 0.5:
                self.optimization_settings["resolution_scale"] *= 0.9
                print(f"  📐 Resolution scale reduced to {self.optimization_settings['resolution_scale']:.2f}")
            
            # Increase confidence threshold (fewer detections)
            if self.optimization_settings["confidence_threshold"] < 0.8:
                self.optimization_settings["confidence_threshold"] += 0.1
                print(f"  🎯 Confidence threshold increased to {self.optimization_settings['confidence_threshold']:.1f}")
        
        elif fps_ratio > 1.2:  # Performance is excellent
            print("✅ Performance above target, increasing quality...")
            
            # Decrease frame skipping
            if self.optimization_settings["frame_skip"] > 1:
                self.optimization_settings["frame_skip"] -= 1
                print(f"  📈 Frame skip reduced to {self.optimization_settings['frame_skip']}")
            
            # Increase resolution
            if self.optimization_settings["resolution_scale"] < 1.0:
                self.optimization_settings["resolution_scale"] = min(1.0, self.optimization_settings["resolution_scale"] * 1.1)
                print(f"  📐 Resolution scale increased to {self.optimization_settings['resolution_scale']:.2f}")
            
            # Decrease confidence threshold (more accurate detections)
            if self.optimization_settings["confidence_threshold"] > 0.3:
                self.optimization_settings["confidence_threshold"] -= 0.05
                print(f"  🎯 Confidence threshold decreased to {self.optimization_settings['confidence_threshold']:.1f}")
    
    def optimize_frame_processing(self, frame):
        """Optimize frame for faster processing"""
        height, width = frame.shape[:2]
        
        # Apply resolution scaling
        scale = self.optimization_settings["resolution_scale"]
        if scale != 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Convert to RGB (YOLO expects RGB)
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame
    
    def threaded_frame_capture(self, cap):
        """Capture frames in separate thread for better performance"""
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                # Skip frame if queue is full
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame)
                except queue.Empty:
                    pass
    
    def get_system_recommendations(self) -> Dict[str, str]:
        """Provide system optimization recommendations"""
        recommendations = {}
        
        metrics = self.monitor_system_performance()
        
        if metrics.cpu_usage > 80:
            recommendations["cpu"] = "🔥 High CPU usage detected. Close unnecessary applications."
        
        if metrics.memory_usage > 80:
            recommendations["memory"] = "💾 High memory usage. Consider restarting the application."
        
        if metrics.gpu_usage and metrics.gpu_usage > 90:
            recommendations["gpu"] = "🎮 GPU overloaded. Reduce resolution or frame rate."
        
        # Check available cores
        cpu_count = psutil.cpu_count(logical=False)
        if cpu_count >= 4:
            recommendations["threading"] = "✅ Multi-core CPU detected. Threading enabled for optimal performance."
        else:
            recommendations["threading"] = "⚠️  Limited CPU cores. Consider single-threaded processing."
        
        return recommendations
    
    def save_performance_profile(self, filename="performance_profile.json"):
        """Save current optimization settings"""
        profile = {
            "optimization_settings": self.optimization_settings,
            "target_fps": self.target_fps,
            "metrics_history": self.metrics_history[-100:]  # Last 100 measurements
        }
        
        with open(filename, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"💾 Performance profile saved to {filename}")
    
    def load_performance_profile(self, filename="performance_profile.json"):
        """Load optimization settings"""
        try:
            with open(filename, 'r') as f:
                profile = json.load(f)
            
            self.optimization_settings = profile.get("optimization_settings", self.optimization_settings)
            self.target_fps = profile.get("target_fps", self.target_fps)
            
            print(f"📂 Performance profile loaded from {filename}")
        except FileNotFoundError:
            print(f"⚠️  Profile file {filename} not found. Using defaults.")

class FPSCounter:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self):
        """Update FPS calculation"""
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Get current FPS"""
        if not self.frame_times:
            return 0
        
        avg_frame_time = np.mean(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0

# Usage example
if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    
    print("🔧 SYSTEM OPTIMIZATION REPORT")
    print("="*40)
    
    # Monitor performance
    metrics = optimizer.monitor_system_performance()
    print(f"CPU Usage: {metrics.cpu_usage:.1f}%")
    print(f"Memory Usage: {metrics.memory_usage:.1f}%")
    if metrics.gpu_usage:
        print(f"GPU Usage: {metrics.gpu_usage:.1f}%")
    
    # Get recommendations
    recommendations = optimizer.get_system_recommendations()
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for category, advice in recommendations.items():
            print(f"  {advice}")
    
    # Show current optimization settings
    print(f"\n⚙️  CURRENT SETTINGS:")
    for setting, value in optimizer.optimization_settings.items():
        print(f"  {setting}: {value}")