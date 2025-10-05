#!/usr/bin/env python3
"""
Advanced Squat Tracker
AI-powered squat form analysis and rep counting
"""

import cv2
import numpy as np
from ultralytics import YOLO
import math
from collections import deque
import matplotlib.pyplot as plt
from datetime import datetime
import json

class AdvancedSquatTracker:
    def __init__(self, model_path="yolo11n-pose.pt"):
        """Initialize the advanced squat tracker"""
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
        self.stage = "up"  # "up" or "down"
        
        # Advanced tracking data
        self.knee_angle_history = deque(maxlen=100)
        self.hip_height_history = deque(maxlen=100)
        self.rep_data = []
        self.current_rep_start = None
        self.current_rep_angles = []
        
        # Squat depth thresholds (knee angle)
        self.DEPTH_THRESHOLDS = {
            'excellent': 90,    # 90° or lower
            'good': 100,        # Around 100°
            'fair': 110,        # Around 110°
            'poor': 120         # 120° or higher
        }
        
        # Squat detection thresholds
        self.ANGLE_THRESHOLDS = {
            'squat_bottom': 110,    # Bottom position (deeper squat)
            'squat_top': 160,       # Top position (standing)
            'min_valid': 80,        # Minimum valid angle
            'max_valid': 180        # Maximum valid angle
        }
        
        # Movement quality metrics
        self.movement_smoothness = 0.0
        self.balance_score = 0.0
        self.depth_consistency = 0.0
        
        # Feedback system
        self.feedback_messages = []
        self.form_score = 0
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points with error handling"""
        try:
            # Validate inputs
            if not all(isinstance(p, (list, tuple, np.ndarray)) and len(p) >= 2 for p in [point1, point2, point3]):
                return None
            
            a = np.array(point1[:2], dtype=float)
            b = np.array(point2[:2], dtype=float)
            c = np.array(point3[:2], dtype=float)
            
            # Check for valid coordinates
            if not all(np.isfinite(coord) for coord in np.concatenate([a, b, c])):
                return None
            
            ba = a - b
            bc = c - b
            
            # Handle zero vectors
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
    
    def get_squat_keypoints(self, keypoints):
        """Get keypoints needed for squat analysis"""
        try:
            # For squats, we need hip, knee, and ankle from both sides
            left_hip = keypoints[self.POSE_KEYPOINTS['left_hip']]
            right_hip = keypoints[self.POSE_KEYPOINTS['right_hip']]
            left_knee = keypoints[self.POSE_KEYPOINTS['left_knee']]
            right_knee = keypoints[self.POSE_KEYPOINTS['right_knee']]
            left_ankle = keypoints[self.POSE_KEYPOINTS['left_ankle']]
            right_ankle = keypoints[self.POSE_KEYPOINTS['right_ankle']]
            
            # Check confidence scores
            points = [left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle]
            if all(point[2] > 0.5 for point in points):
                return left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle
            return None, None, None, None, None, None
        except Exception:
            return None, None, None, None, None, None
    
    def analyze_squat_depth(self, knee_angle):
        """Analyze squat depth quality"""
        if knee_angle is None:
            return "unknown", 0
        
        if knee_angle <= self.DEPTH_THRESHOLDS['excellent']:
            return "excellent", 100
        elif knee_angle <= self.DEPTH_THRESHOLDS['good']:
            return "good", 85
        elif knee_angle <= self.DEPTH_THRESHOLDS['fair']:
            return "fair", 70
        else:
            return "poor", 50
    
    def analyze_squat_advanced(self, keypoints):
        """Advanced squat analysis with detailed metrics"""
        try:
            # Validate input keypoints
            if keypoints is None or len(keypoints) < 17:
                return None, ["❌ Incomplete pose data"]
            
            # Get squat keypoints
            try:
                left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle = self.get_squat_keypoints(keypoints)
            except Exception:
                return None, ["❌ Error accessing keypoints"]
            
            if left_hip is None:
                return None, ["❌ Cannot detect leg keypoints clearly"]
            
            # Calculate knee angles (use the clearer side)
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            # Use the more reliable angle
            knee_angle = None
            if left_knee_angle is not None and right_knee_angle is not None:
                knee_angle = (left_knee_angle + right_knee_angle) / 2
            elif left_knee_angle is not None:
                knee_angle = left_knee_angle
            elif right_knee_angle is not None:
                knee_angle = right_knee_angle
            
            if knee_angle is None:
                return None, ["❌ Cannot calculate knee angle"]
            
            # Validate angle
            if not (self.ANGLE_THRESHOLDS['min_valid'] <= knee_angle <= self.ANGLE_THRESHOLDS['max_valid']):
                return None, ["⚠️ Invalid angle detected - adjust position"]
            
            # Store tracking data
            try:
                self.knee_angle_history.append(knee_angle)
                
                # Calculate hip height for balance analysis
                avg_hip_y = (left_hip[1] + right_hip[1]) / 2
                self.hip_height_history.append(avg_hip_y)
            except Exception:
                pass
            
            feedback = []
            
            # Rep detection logic
            try:
                if knee_angle < self.ANGLE_THRESHOLDS['squat_bottom']:  # Bottom position
                    if self.stage == "up":
                        # Rep completed
                        self.rep_count += 1
                        self.stage = "down"
                        
                        # Save progress for API communication
                        self.save_progress()
                        
                        # Analyze the completed rep
                        rep_analysis = self.analyze_completed_squat_rep(knee_angle)
                        feedback.extend(rep_analysis)
                
                elif knee_angle > self.ANGLE_THRESHOLDS['squat_top']:  # Top position
                    self.stage = "up"
                
                # Real-time feedback
                depth_quality, depth_score = self.analyze_squat_depth(knee_angle)
                
                if depth_quality == "poor":
                    feedback.append("⬇️ Go deeper - squat down more")
                elif depth_quality == "excellent":
                    feedback.append("✅ Perfect depth!")
                
                # Balance feedback (check hip stability)
                if len(self.hip_height_history) > 10:
                    hip_stability = np.std(list(self.hip_height_history)[-10:])
                    if hip_stability > 20:
                        feedback.append("⚖️ Keep your balance - control the movement")
                
            except Exception:
                feedback.append("⚠️ Processing error - continuing tracking")
            
            return knee_angle, feedback
            
        except Exception:
            return None, ["❌ Tracking error - please reposition"]
    
    def analyze_completed_squat_rep(self, final_angle):
        """Analyze a completed squat repetition"""
        feedback = []
        
        try:
            depth_quality, depth_score = self.analyze_squat_depth(final_angle)
            
            if depth_quality == "excellent":
                feedback.append("🎯 Excellent depth!")
            elif depth_quality == "good":
                feedback.append("👍 Good depth")
            elif depth_quality == "fair":
                feedback.append("📐 Try to go a bit deeper")
            else:
                feedback.append("⬇️ Need more depth - squat lower")
            
            # Store rep data
            rep_info = {
                'rep_number': self.rep_count,
                'depth_angle': final_angle,
                'depth_quality': depth_quality,
                'depth_score': depth_score,
                'timestamp': datetime.now().isoformat()
            }
            self.rep_data.append(rep_info)
            
        except Exception:
            feedback.append("✅ Rep completed")
        
        return feedback
    
    def draw_squat_pose_info(self, frame, keypoints, knee_angle):
        """Draw squat-specific pose information"""
        try:
            if keypoints is None or len(keypoints) < 17:
                return
            
            # Get keypoints
            left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle = self.get_squat_keypoints(keypoints)
            
            if left_hip is None:
                return
            
            # Draw skeleton connections for legs
            connections = [
                (left_hip, left_knee), (left_knee, left_ankle),
                (right_hip, right_knee), (right_knee, right_ankle),
                (left_hip, right_hip)
            ]
            
            for point1, point2 in connections:
                if point1[2] > 0.5 and point2[2] > 0.5:
                    pt1 = (int(point1[0]), int(point1[1]))
                    pt2 = (int(point2[0]), int(point2[1]))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
            
            # Draw keypoints
            for point in [left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle]:
                if point[2] > 0.5:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 8, (255, 0, 0), -1)
            
            # Draw knee angle visualization
            if knee_angle and left_knee[2] > 0.5:
                self.draw_angle_indicator(frame, left_hip, left_knee, left_ankle, knee_angle)
                
        except Exception:
            pass
    
    def draw_angle_indicator(self, frame, hip, knee, ankle, angle):
        """Draw angle indicator at knee"""
        try:
            if not all(isinstance(p, (list, tuple, np.ndarray)) and len(p) >= 2 for p in [hip, knee, ankle]):
                return
            
            height, width = frame.shape[:2]
            knee_x, knee_y = int(knee[0]), int(knee[1])
            
            if not (0 <= knee_x < width and 0 <= knee_y < height):
                return
            
            # Draw angle arc
            radius = 40
            cv2.circle(frame, (knee_x, knee_y), radius, (255, 255, 0), 2)
            
            # Draw angle text
            text_x = max(0, min(width - 100, knee_x + 50))
            text_y = max(30, min(height - 10, knee_y - 30))
            
            cv2.putText(frame, f'{angle:.1f}°', (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        except Exception:
            pass
    
    def draw_squat_ui(self, frame, knee_angle):
        """Draw squat-specific UI"""
        try:
            height, width = frame.shape[:2]
            
            # Main info panel
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (320, 160), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
            
            # Title
            cv2.putText(frame, 'Advanced Squat Tracker', 
                       (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Basic stats
            cv2.putText(frame, f'Reps: {self.rep_count}', 
                       (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            stage_color = (0, 255, 255) if self.stage == "down" else (255, 255, 0)
            cv2.putText(frame, f'Stage: {self.stage.upper()}', 
                       (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, stage_color, 2)
            
            # Current angle
            if knee_angle:
                depth_quality, depth_score = self.analyze_squat_depth(knee_angle)
                angle_color = (0, 255, 0) if depth_quality in ['excellent', 'good'] else (0, 165, 255) if depth_quality == 'fair' else (0, 0, 255)
                
                cv2.putText(frame, f'Knee Angle: {knee_angle:.1f}°', 
                           (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, angle_color, 2)
                
                cv2.putText(frame, f'Depth: {depth_quality.title()}', 
                           (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, angle_color, 2)
            
            # Feedback messages
            y_offset = 170
            for i, message in enumerate(self.feedback_messages[-2:]):
                cv2.putText(frame, message, (20, y_offset + i * 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        except Exception:
            pass
    
    def save_progress(self):
        """Save current progress to file for API communication"""
        try:
            progress_data = {
                "rep_count": self.rep_count,
                "stage": self.stage,
                "timestamp": datetime.now().isoformat()
            }
            with open("squats_progress.json", "w") as f:
                json.dump(progress_data, f)
        except Exception as e:
            # Don't let progress saving errors crash the tracker
            pass
    
    def run_squat_tracking(self):
        """Run the squat tracking system with crash protection"""
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("Advanced Squat Tracker Started!")
            print("")
            print("📐 POSITIONING INSTRUCTIONS:")
            print("  🎯 Stand facing the camera (front view)")
            print("  📏 Make sure your full body is visible")
            print("  🚶 Stand 4-5 feet from camera")
            print("  💡 Ensure good lighting from front")
            print("  🦵 Keep feet shoulder-width apart")
            print("")
            print("🏋️ SQUAT FORM TIPS:")
            print("  📐 Squat down until thighs are parallel to floor")
            print("  👀 Keep chest up and back straight")
            print("  🦵 Push knees out, don't let them cave in")
            print("  ⚖️ Keep weight balanced on your feet")
            print("")
            print("Controls:")
            print("  'q' - Quit")
            print("  'r' - Reset rep count")
            
            frame_count = 0
            error_count = 0
            max_errors = 50
            
            while True:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        error_count += 1
                        if error_count > max_errors:
                            print("Camera error - stopping...")
                            break
                        continue
                    
                    frame_count += 1
                    error_count = 0
                    
                    if frame is None or frame.size == 0:
                        continue
                    
                    try:
                        frame = cv2.flip(frame, 1)
                    except Exception:
                        continue
                    
                    # Run pose estimation
                    try:
                        results = self.model(frame, conf=0.5, verbose=False)
                        
                        if (results and len(results) > 0 and 
                            results[0].keypoints is not None and 
                            len(results[0].keypoints.data) > 0):
                            
                            keypoints = results[0].keypoints.data[0].cpu().numpy()
                            
                            if keypoints is not None and len(keypoints) >= 17:
                                try:
                                    result = self.analyze_squat_advanced(keypoints)
                                    if result and len(result) == 2:
                                        knee_angle, feedback = result
                                        if feedback and isinstance(feedback, list):
                                            self.feedback_messages = feedback[-2:]
                                        else:
                                            self.feedback_messages = ["✅ Tracking active"]
                                    else:
                                        knee_angle = None
                                        self.feedback_messages = ["⚠️ Analysis error"]
                                except Exception as e:
                                    self.feedback_messages = ["⚠️ Processing error"]
                                    knee_angle = None
                                
                                try:
                                    self.draw_squat_pose_info(frame, keypoints, knee_angle)
                                except Exception:
                                    pass
                            else:
                                self.feedback_messages = ["⚠️ Incomplete pose data"]
                                knee_angle = None
                        else:
                            self.feedback_messages = ["❌ No person detected"]
                            knee_angle = None
                    
                    except Exception as e:
                        self.feedback_messages = ["⚠️ Detection error"]
                        knee_angle = None
                    
                    # Draw UI
                    try:
                        self.draw_squat_ui(frame, knee_angle)
                    except Exception:
                        # Draw minimal fallback UI
                        try:
                            cv2.putText(frame, f'Reps: {self.rep_count}', (20, 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        except:
                            pass
                    
                    # Display frame
                    try:
                        cv2.imshow('Advanced Squat Tracker', frame)
                    except Exception:
                        continue
                    
                    # Save progress periodically (every 30 frames = ~1 second)
                    if frame_count % 30 == 0:
                        self.save_progress()
                    
                    # Handle key presses
                    try:
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                        elif key == ord('r'):
                            self.rep_count = 0
                            self.rep_data = []
                            self.knee_angle_history.clear()
                            self.hip_height_history.clear()
                            print("Session reset!")
                    except Exception:
                        pass
                    
                    # Memory management
                    if frame_count % 1000 == 0:
                        print(f"Processed {frame_count} frames")
                        if len(self.knee_angle_history) > 200:
                            self.knee_angle_history = deque(list(self.knee_angle_history)[-100:], maxlen=100)
                        if len(self.hip_height_history) > 200:
                            self.hip_height_history = deque(list(self.hip_height_history)[-100:], maxlen=100)
                
                except KeyboardInterrupt:
                    print("\nStopping tracker...")
                    break
                except Exception as e:
                    error_count += 1
                    if error_count > max_errors:
                        print("Too many errors - stopping...")
                        break
                    continue
        
        except Exception as e:
            print(f"Fatal error: {e}")
        
        finally:
            try:
                if cap is not None:
                    cap.release()
                cv2.destroyAllWindows()
                print("Camera closed successfully")
            except Exception:
                pass
            
            # Show final stats
            try:
                if self.rep_data:
                    print(f"\n🎯 SESSION COMPLETE!")
                    print(f"Total Reps: {self.rep_count}")
                    if self.rep_data:
                        avg_depth = np.mean([rep['depth_score'] for rep in self.rep_data])
                        print(f"Average Depth Score: {avg_depth:.1f}%")
            except Exception:
                pass

if __name__ == "__main__":
    tracker = AdvancedSquatTracker()
    tracker.run_squat_tracking()