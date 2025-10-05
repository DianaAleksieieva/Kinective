#!/usr/bin/env python3
"""
Real-time Performance Dashboard for Exercise Tracking
Live visualization of exercise metrics and progress
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue
from collections import deque
import time

class ExerciseDashboard:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.angle_history = deque(maxlen=100)
        self.rep_times = deque(maxlen=10)
        self.form_scores = deque(maxlen=10)
        
        # Dashboard metrics
        self.current_rpm = 0  # Reps per minute
        self.avg_form_score = 0
        self.workout_duration = 0
        self.calories_burned = 0
        
        # Real-time plotting
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.setup_plots()
        
    def setup_plots(self):
        """Setup the dashboard plots"""
        # Angle tracking plot
        self.axes[0, 0].set_title('Real-time Angle Tracking')
        self.axes[0, 0].set_xlabel('Time (frames)')
        self.axes[0, 0].set_ylabel('Angle (degrees)')
        self.axes[0, 0].set_ylim(0, 180)
        
        # Form score plot
        self.axes[0, 1].set_title('Form Score History')
        self.axes[0, 1].set_xlabel('Rep Number')
        self.axes[0, 1].set_ylabel('Form Score (%)')
        self.axes[0, 1].set_ylim(0, 100)
        
        # Rep tempo plot
        self.axes[1, 0].set_title('Rep Tempo (RPM)')
        self.axes[1, 0].set_xlabel('Time')
        self.axes[1, 0].set_ylabel('Reps per Minute')
        
        # Calories burned
        self.axes[1, 1].set_title('Workout Summary')
        self.axes[1, 1].axis('off')
        
    def update_metrics(self, angle, rep_completed, form_score):
        """Update dashboard metrics"""
        self.angle_history.append(angle)
        
        if rep_completed:
            current_time = time.time()
            self.rep_times.append(current_time)
            self.form_scores.append(form_score)
            
            # Calculate RPM
            if len(self.rep_times) >= 2:
                time_diff = self.rep_times[-1] - self.rep_times[0]
                self.current_rpm = len(self.rep_times) * 60 / time_diff if time_diff > 0 else 0
            
            # Calculate calories (rough estimate)
            self.calories_burned += 0.5  # ~0.5 calories per rep
        
        self.avg_form_score = np.mean(self.form_scores) if self.form_scores else 0
    
    def create_overlay(self, frame):
        """Create performance overlay for video feed"""
        overlay = frame.copy()
        
        # Create semi-transparent background
        cv2.rectangle(overlay, (10, 10), (320, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Add metrics text
        metrics = [
            f"RPM: {self.current_rpm:.1f}",
            f"Avg Form Score: {self.avg_form_score:.1f}%",
            f"Calories: {self.calories_burned:.1f}",
            f"Total Reps: {len(self.form_scores)}"
        ]
        
        y_offset = 35
        for metric in metrics:
            cv2.putText(frame, metric, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 25
            
        return frame