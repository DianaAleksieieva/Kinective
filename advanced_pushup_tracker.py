#!/usr/bin/env python3
"""
Advanced Push-up Tracker using YOLO11-pose
Real-time push-up form analysis with pose estimation
"""

import cv2
import numpy as np
import math
import time
from ultralytics import YOLO
import matplotlib.pyplot as plt
from collections import deque
import csv
from datetime import datetime

class AdvancedPushupTracker:
    def __init__(self):
        print("Loading YOLO11-pose model...")
        self.model = YOLO('yolo11n-pose.pt')
        
        # Push-up tracking variables
        self.rep_count = 0
        self.in_down_position = False
        self.min_angle_threshold = 90  # Minimum elbow angle for "down"
        self.max_angle_threshold = 160  # Maximum elbow angle for "up"
        
        # Data smoothing and filtering
        self.angle_smoothing_window = 5  # Smooth over 5 frames
        self.confidence_threshold = 0.7  # Require high confidence keypoints
        self.min_keypoints_required = 6  # Need at least 6 good keypoints
        
        # Data storage for analysis
        self.angle_history = deque(maxlen=100)
        self.smoothed_angles = deque(maxlen=self.angle_smoothing_window)
        self.rep_data = []
        self.session_start = datetime.now()
        
        # Form analysis
        self.form_scores = []
        self.body_alignment_scores = []
        
        # Display settings
        self.show_analytics = False
        
    def filter_low_confidence_keypoints(self, keypoints):
        """Filter out low confidence keypoints and validate pose"""
        # Count high-confidence keypoints
        high_conf_count = sum(1 for kp in keypoints if kp[2] > self.confidence_threshold)
        
        if high_conf_count < self.min_keypoints_required:
            return None  # Not enough good keypoints
        
        # Check if essential keypoints for push-ups are detected
        essential_points = [5, 6, 7, 8, 9, 10]  # Shoulders, elbows, wrists
        essential_detected = sum(1 for idx in essential_points if keypoints[idx][2] > self.confidence_threshold)
        
        if essential_detected < 4:  # Need at least 4 of 6 essential points
            return None
        
        return keypoints
    
    def smooth_angle(self, new_angle):
        """Apply smoothing to angle measurements"""
        if new_angle > 0:
            self.smoothed_angles.append(new_angle)
            return np.mean(list(self.smoothed_angles))
        return 0
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            p1 = np.array(point1)
            p2 = np.array(point2)  # Vertex
            p3 = np.array(point3)
            
            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.degrees(np.arccos(cos_angle))
            
            return angle
        except:
            return 0
    
    def calculate_body_alignment(self, keypoints):
        """Calculate body alignment score (head-shoulder-hip-ankle line)"""
        try:
            # Get keypoints for body alignment
            head = keypoints[0]  # Nose
            shoulder = keypoints[5]  # Left shoulder
            hip = keypoints[11]  # Left hip
            ankle = keypoints[15]  # Left ankle
            
            # Check if all keypoints are detected
            if all(kp[2] > 0.5 for kp in [head, shoulder, hip, ankle]):
                # Calculate alignment score based on how straight the line is
                points = np.array([[head[0], head[1]], 
                                 [shoulder[0], shoulder[1]], 
                                 [hip[0], hip[1]], 
                                 [ankle[0], ankle[1]]])
                
                # Fit a line and calculate deviation
                x_coords = points[:, 0]
                y_coords = points[:, 1]
                
                # Simple alignment check - calculate variance from best fit line
                if len(x_coords) > 1:
                    line_fit = np.polyfit(y_coords, x_coords, 1)
                    predicted_x = np.polyval(line_fit, y_coords)
                    deviation = np.mean(np.abs(x_coords - predicted_x))
                    
                    # Convert to score (lower deviation = higher score)
                    alignment_score = max(0, 100 - deviation * 2)
                    return min(100, alignment_score)
            
            return 0
        except:
            return 0
    
    def analyze_pushup_form(self, keypoints):
        """Analyze push-up form and provide feedback"""
        try:
            # First filter keypoints for quality
            filtered_kpts = self.filter_low_confidence_keypoints(keypoints)
            if filtered_kpts is None:
                return {'elbow_angle': 0, 'body_alignment': 0, 'rep_completed': False, 'in_down_position': self.in_down_position, 'quality': 'poor'}
            
            # Get relevant keypoints
            left_shoulder = filtered_kpts[5]
            left_elbow = filtered_kpts[7]
            left_wrist = filtered_kpts[9]
            right_shoulder = filtered_kpts[6]
            right_elbow = filtered_kpts[8]
            right_wrist = filtered_kpts[10]
            
            # Only calculate if we have high confidence in these points
            if not all(kp[2] > self.confidence_threshold for kp in [left_shoulder, left_elbow, left_wrist, right_shoulder, right_elbow, right_wrist]):
                return {'elbow_angle': 0, 'body_alignment': 0, 'rep_completed': False, 'in_down_position': self.in_down_position, 'quality': 'low_confidence'}
            
            # Calculate elbow angles
            left_angle = self.calculate_angle(left_shoulder[:2], left_elbow[:2], left_wrist[:2])
            right_angle = self.calculate_angle(right_shoulder[:2], right_elbow[:2], right_wrist[:2])
            
            # Average the angles
            raw_angle = (left_angle + right_angle) / 2 if left_angle > 0 and right_angle > 0 else 0
            
            # Apply smoothing
            avg_elbow_angle = self.smooth_angle(raw_angle)
            
            # Calculate body alignment
            body_alignment = self.calculate_body_alignment(filtered_kpts)
            
            # Store angle history
            if avg_elbow_angle > 0:
                self.angle_history.append(avg_elbow_angle)
            
            # Rep counting logic with improved thresholds
            current_down = avg_elbow_angle < self.min_angle_threshold and avg_elbow_angle > 60  # Prevent false positives
            current_up = avg_elbow_angle > self.max_angle_threshold
            
            rep_completed = False
            
            if current_down and not self.in_down_position:
                self.in_down_position = True
            elif current_up and self.in_down_position:
                self.in_down_position = False
                self.rep_count += 1
                rep_completed = True
                
                # Store rep data
                rep_data = {
                    'rep_number': self.rep_count,
                    'timestamp': time.time(),
                    'min_angle': min(list(self.angle_history)[-20:]) if self.angle_history else 0,
                    'max_angle': max(list(self.angle_history)[-20:]) if self.angle_history else 0,
                    'body_alignment': body_alignment,
                    'form_score': self.calculate_form_score(avg_elbow_angle, body_alignment)
                }
                self.rep_data.append(rep_data)
            
            return {
                'elbow_angle': avg_elbow_angle,
                'body_alignment': body_alignment,
                'rep_completed': rep_completed,
                'in_down_position': self.in_down_position,
                'quality': 'good'
            }
            
        except Exception as e:
            print(f"Error in form analysis: {e}")
            return {'elbow_angle': 0, 'body_alignment': 0, 'rep_completed': False, 'in_down_position': False, 'quality': 'error'}
    
    def calculate_form_score(self, elbow_angle, body_alignment):
        """Calculate overall form score"""
        # Elbow angle component (0-50 points)
        if 70 <= elbow_angle <= 90:  # Good depth
            angle_score = 50
        elif 60 <= elbow_angle < 70 or 90 < elbow_angle <= 100:  # Decent depth
            angle_score = 35
        else:  # Poor depth
            angle_score = 10
        
        # Body alignment component (0-50 points)
        alignment_score = body_alignment * 0.5
        
        total_score = angle_score + alignment_score
        return min(100, total_score)
    
    def draw_pose_landmarks(self, frame, keypoints):
        """Draw pose landmarks and connections"""
        # Define connections for pose skeleton
        connections = [
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
            (5, 11), (6, 12), (11, 12),  # Torso
            (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
        ]
        
        # Draw keypoints
        for i, (x, y, conf) in enumerate(keypoints):
            if conf > 0.5:
                cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
        
        # Draw connections
        for start_idx, end_idx in connections:
            if (keypoints[start_idx][2] > 0.5 and keypoints[end_idx][2] > 0.5):
                start_point = (int(keypoints[start_idx][0]), int(keypoints[start_idx][1]))
                end_point = (int(keypoints[end_idx][0]), int(keypoints[end_idx][1]))
                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
    
    def draw_analytics(self, frame):
        """Draw analytics overlay"""
        if not self.show_analytics or not self.rep_data:
            return
        
        # Create analytics text
        y_offset = 30
        analytics_text = [
            f"Total Reps: {len(self.rep_data)}",
            f"Average Form Score: {np.mean([rep['form_score'] for rep in self.rep_data]):.1f}",
            f"Best Rep Score: {max([rep['form_score'] for rep in self.rep_data]):.1f}",
            f"Average Body Alignment: {np.mean([rep['body_alignment'] for rep in self.rep_data]):.1f}%"
        ]
        
        for text in analytics_text:
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
    
    def export_session_data(self):
        """Export session data to CSV"""
        if not self.rep_data:
            print("No rep data to export!")
            return
        
        filename = f"pushup_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['rep_number', 'timestamp', 'min_angle', 'max_angle', 'body_alignment', 'form_score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for rep in self.rep_data:
                writer.writerow(rep)
        
        print(f"Session data exported to {filename}")
    
    def run_advanced_tracking(self):
        """Main tracking loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Advanced Push-up Tracker Started!")
        print("Controls:")
        print("  'q' - Quit")
        print("  'r' - Reset rep count")
        print("  'a' - Toggle analytics")
        print("  'e' - Export session data")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Run YOLO pose detection with higher confidence threshold
            results = self.model(frame, conf=0.7, verbose=False)  # Increased from 0.5 to 0.7
            
            if results[0].keypoints is not None:
                for keypoints in results[0].keypoints.data:
                    # Convert to numpy array
                    kpts = keypoints.cpu().numpy()
                    
                    # Analyze push-up form
                    analysis = self.analyze_pushup_form(kpts)
                    
                    # Draw pose landmarks
                    self.draw_pose_landmarks(frame, kpts)
                    
                    # Draw form feedback
                    elbow_angle = analysis['elbow_angle']
                    body_alignment = analysis['body_alignment']
                    
                    # Status display
                    status = "DOWN" if analysis['in_down_position'] else "UP"
                    status_color = (0, 255, 255) if analysis['in_down_position'] else (255, 0, 255)
                    
                    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                    cv2.putText(frame, f"Reps: {self.rep_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if elbow_angle > 0:
                        cv2.putText(frame, f"Elbow Angle: {elbow_angle:.1f}°", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    if body_alignment > 0:
                        cv2.putText(frame, f"Body Alignment: {body_alignment:.1f}%", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Form feedback
                    if analysis['rep_completed']:
                        cv2.putText(frame, "REP COMPLETED!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)
            
            # Draw analytics if enabled
            self.draw_analytics(frame)
            
            cv2.imshow('Advanced Push-up Tracker', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.rep_count = 0
                self.rep_data = []
                self.angle_history.clear()
                print("Rep count reset!")
            elif key == ord('a'):
                self.show_analytics = not self.show_analytics
                print(f"Analytics {'enabled' if self.show_analytics else 'disabled'}")
            elif key == ord('e'):
                self.export_session_data()
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = AdvancedPushupTracker()
    tracker.run_advanced_tracking()