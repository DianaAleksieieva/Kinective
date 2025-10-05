#!/usr/bin/env python3
"""
Advanced Shoulder Press Tracker
AI-powered shoulder press form analysis and rep counting
"""

import cv2
import numpy as np
from ultralytics import YOLO
import math
from collections import deque
from datetime import datetime

class AdvancedShoulderPressTracker:
    def __init__(self, model_path="yolo11n-pose.pt"):
        """Initialize the advanced shoulder press tracker"""
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
        self.stage = "down"
        
        # Advanced tracking data
        self.arm_angle_history = deque(maxlen=100)
        self.rep_data = []
        self.feedback_messages = []
        
        # Shoulder press thresholds
        self.ANGLE_THRESHOLDS = {
            'press_top': 160,       # Arms extended overhead
            'press_bottom': 90,     # Starting position
            'min_valid': 60,
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
    
    def analyze_shoulder_press_advanced(self, keypoints):
        """Advanced shoulder press analysis"""
        try:
            if keypoints is None or len(keypoints) < 17:
                return None, ["❌ Incomplete pose data"]
            
            # Get right arm keypoints (can be modified for left arm)
            shoulder = keypoints[self.POSE_KEYPOINTS['right_shoulder']]
            elbow = keypoints[self.POSE_KEYPOINTS['right_elbow']]
            wrist = keypoints[self.POSE_KEYPOINTS['right_wrist']]
            
            if not all(point[2] > 0.5 for point in [shoulder, elbow, wrist]):
                return None, ["❌ Cannot detect arm keypoints clearly"]
            
            # Calculate shoulder angle (shoulder-elbow-wrist)
            arm_angle = self.calculate_angle(shoulder, elbow, wrist)
            if arm_angle is None:
                return None, ["❌ Cannot calculate arm angle"]
            
            if not (self.ANGLE_THRESHOLDS['min_valid'] <= arm_angle <= self.ANGLE_THRESHOLDS['max_valid']):
                return None, ["⚠️ Invalid angle - adjust position"]
            
            self.arm_angle_history.append(arm_angle)
            feedback = []
            
            # Rep detection logic
            if arm_angle > self.ANGLE_THRESHOLDS['press_top']:  # Arms overhead
                if self.stage == "down":
                    self.rep_count += 1
                    self.stage = "up"
                    feedback.append("✅ Good press! Full range of motion")
            elif arm_angle < self.ANGLE_THRESHOLDS['press_bottom']:  # Starting position
                self.stage = "down"
            
            # Form feedback
            if self.stage == "up" and arm_angle < 150:
                feedback.append("⬆️ Press higher - full extension")
            elif self.stage == "down" and arm_angle > 120:
                feedback.append("⬇️ Lower the weight to starting position")
            
            return arm_angle, feedback
            
        except Exception:
            return None, ["❌ Tracking error"]
    
    def draw_shoulder_press_ui(self, frame, arm_angle):
        """Draw shoulder press specific UI"""
        try:
            # Main info panel
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            
            cv2.putText(frame, 'Advanced Shoulder Press Tracker', 
                       (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(frame, f'Reps: {self.rep_count}', 
                       (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            stage_color = (0, 255, 255) if self.stage == "up" else (255, 255, 0)
            cv2.putText(frame, f'Stage: {self.stage.upper()}', 
                       (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, stage_color, 2)
            
            if arm_angle:
                cv2.putText(frame, f'Arm Angle: {arm_angle:.1f}°', 
                           (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        except Exception:
            pass
    
    def run_shoulder_press_tracking(self):
        """Run the shoulder press tracking system"""
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return
            
            print("Advanced Shoulder Press Tracker Started!")
            print("📐 Stand facing camera with weights or dumbbells")
            print("🏋️ Press weights overhead for full range of motion")
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
                        
                        result = self.analyze_shoulder_press_advanced(keypoints)
                        if result and len(result) == 2:
                            arm_angle, feedback = result
                            if feedback:
                                self.feedback_messages = feedback[-2:]
                        else:
                            arm_angle = None
                            self.feedback_messages = ["❌ No person detected"]
                    else:
                        arm_angle = None
                        self.feedback_messages = ["❌ No person detected"]
                
                except Exception:
                    arm_angle = None
                    self.feedback_messages = ["⚠️ Detection error"]
                
                self.draw_shoulder_press_ui(frame, arm_angle)
                
                cv2.imshow('Advanced Shoulder Press Tracker', frame)
                
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
    tracker = AdvancedShoulderPressTracker()
    tracker.run_shoulder_press_tracking()