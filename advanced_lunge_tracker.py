#!/usr/bin/env python3
"""
Advanced Lunge Tracker
AI-powered lunge form analysis and rep counting
"""

import cv2
import numpy as np
from ultralytics import YOLO
import math
from collections import deque
from datetime import datetime

class AdvancedLungeTracker:
    def __init__(self, model_path="yolo11n-pose.pt"):
        """Initialize the advanced lunge tracker"""
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            return
        
        # COCO pose keypoint indices
        self.POSE_KEYPOINTS = {
            'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
            'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
            'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
        }
        
        # Exercise tracking variables
        self.rep_count = 0
        self.stage = "up"
        self.active_leg = "right"  # Which leg is stepping forward
        
        # Advanced tracking data
        self.knee_angle_history = deque(maxlen=100)
        self.rep_data = []
        self.feedback_messages = []
        
        # Lunge thresholds
        self.ANGLE_THRESHOLDS = {
            'lunge_bottom': 100,    # Bottom position
            'lunge_top': 150,       # Top position
            'min_valid': 70,
            'max_valid': 180
        }
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        try:
            a = np.array(point1[:2], dtype=float)
            b = np.array(point2[:2], dtype=float)
            c = np.array(point3[:2], dtype=float)
            
            if not all(np.isfinite(coord) for coord in np.concatenate([a, b, c])):
                return None
            
            ba = a - b
            bc = c - b
            
            ba_norm = np.linalg.norm(ba)
            bc_norm = np.linalg.norm(bc)
            
            if ba_norm < 1e-6 or bc_norm < 1e-6:
                return None
            
            cosine_angle = np.dot(ba, bc) / (ba_norm * bc_norm)
            cosine_angle = np.clip(cosine_angle, -1, 1)
            
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)
        except Exception:
            return None
    
    def analyze_lunge_advanced(self, keypoints):
        """Advanced lunge analysis"""
        try:
            if keypoints is None or len(keypoints) < 17:
                return None, ["❌ Incomplete pose data"]
            
            # Get front leg keypoints (assume right leg forward for now)
            hip = keypoints[self.POSE_KEYPOINTS['right_hip']]
            knee = keypoints[self.POSE_KEYPOINTS['right_knee']]
            ankle = keypoints[self.POSE_KEYPOINTS['right_ankle']]
            
            if not all(point[2] > 0.5 for point in [hip, knee, ankle]):
                return None, ["❌ Cannot detect leg keypoints clearly"]
            
            knee_angle = self.calculate_angle(hip, knee, ankle)
            if knee_angle is None:
                return None, ["❌ Cannot calculate knee angle"]
            
            if not (self.ANGLE_THRESHOLDS['min_valid'] <= knee_angle <= self.ANGLE_THRESHOLDS['max_valid']):
                return None, ["⚠️ Invalid angle - adjust position"]
            
            self.knee_angle_history.append(knee_angle)
            feedback = []
            
            # Rep detection
            if knee_angle < self.ANGLE_THRESHOLDS['lunge_bottom']:
                if self.stage == "up":
                    self.rep_count += 1
                    self.stage = "down"
                    feedback.append("✅ Good lunge depth!")
            elif knee_angle > self.ANGLE_THRESHOLDS['lunge_top']:
                self.stage = "up"
            
            # Form feedback
            if knee_angle > 130:
                feedback.append("⬇️ Lunge deeper for better form")
            
            return knee_angle, feedback
            
        except Exception:
            return None, ["❌ Tracking error"]
    
    def draw_lunge_ui(self, frame, knee_angle):
        """Draw lunge-specific UI"""
        try:
            # Main info panel
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (350, 150), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            
            cv2.putText(frame, 'Advanced Lunge Tracker', 
                       (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(frame, f'Reps: {self.rep_count}', 
                       (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            stage_color = (0, 255, 255) if self.stage == "down" else (255, 255, 0)
            cv2.putText(frame, f'Stage: {self.stage.upper()}', 
                       (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, stage_color, 2)
            
            if knee_angle:
                cv2.putText(frame, f'Knee Angle: {knee_angle:.1f}°', 
                           (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        except Exception:
            pass
    
    def run_lunge_tracking(self):
        """Run the lunge tracking system"""
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return
            
            print("Advanced Lunge Tracker Started!")
            print("📐 Stand sideways to camera for best tracking")
            print("🦵 Step forward into lunge position")
            print("Controls: 'q' to quit, 'r' to reset")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                
                try:
                    results = self.model(frame, conf=0.5, verbose=False)
                    
                    if (results and len(results) > 0 and 
                        results[0].keypoints is not None and 
                        len(results[0].keypoints.data) > 0):
                        
                        keypoints = results[0].keypoints.data[0].cpu().numpy()
                        
                        result = self.analyze_lunge_advanced(keypoints)
                        if result and len(result) == 2:
                            knee_angle, feedback = result
                            if feedback:
                                self.feedback_messages = feedback[-2:]
                        else:
                            knee_angle = None
                            self.feedback_messages = ["❌ No person detected"]
                    else:
                        knee_angle = None
                        self.feedback_messages = ["❌ No person detected"]
                
                except Exception:
                    knee_angle = None
                    self.feedback_messages = ["⚠️ Detection error"]
                
                self.draw_lunge_ui(frame, knee_angle)
                
                cv2.imshow('Advanced Lunge Tracker', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.rep_count = 0
                    print("Session reset!")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            print(f"Session complete! Total reps: {self.rep_count}")

if __name__ == "__main__":
    tracker = AdvancedLungeTracker()
    tracker.run_lunge_tracking()