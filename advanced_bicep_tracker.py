import cv2
import numpy as np
from ultralytics import YOLO
import math
from collections import deque
import matplotlib.pyplot as plt
from datetime import datetime
import json

class AdvancedBicepTracker:
    def __init__(self, model_path="yolo11n-pose.pt"):
        """Initialize the advanced bicep curl tracker"""
        self.model = YOLO(model_path)
        
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
        self.active_arm = "right"  # Can switch between "left" and "right"
        
        # Advanced tracking data
        self.angle_history = deque(maxlen=100)  # Store last 100 angle measurements
        self.elbow_position_history = deque(maxlen=50)  # Track elbow stability
        self.rep_data = []  # Store detailed rep analysis
        self.current_rep_start = None
        self.current_rep_angles = []
        
        # Range of motion thresholds (optimized for 90° side view)
        self.ROM_THRESHOLDS = {
            'excellent': {'min': 35, 'max': 165},  # Near full ROM
            'good': {'min': 45, 'max': 155},       # Good ROM
            'fair': {'min': 55, 'max': 145},       # Acceptable ROM
            'poor': {'min': 65, 'max': 135}        # Limited ROM
        }
        
        # Optimized angle detection thresholds for side view
        self.ANGLE_THRESHOLDS = {
            'contracted': 50,    # Bicep fully contracted (up position)
            'extended': 160,     # Arm nearly straight (down position)
            'min_valid': 30,     # Minimum valid angle (filters bad detections)
            'max_valid': 180     # Maximum valid angle
        }
        
        # Movement quality metrics
        self.movement_smoothness = 0.0
        self.tempo_consistency = 0.0
        self.elbow_stability_score = 0.0
        
        # Feedback system
        self.feedback_messages = []
        self.form_score = 0
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points with error handling"""
        try:
            a = np.array(point1[:2])  # Only use x, y coordinates
            b = np.array(point2[:2])
            c = np.array(point3[:2])
            
            ba = a - b
            bc = c - b
            
            # Handle zero vectors
            ba_norm = np.linalg.norm(ba)
            bc_norm = np.linalg.norm(bc)
            
            if ba_norm == 0 or bc_norm == 0:
                return None
            
            cosine_angle = np.dot(ba, bc) / (ba_norm * bc_norm)
            cosine_angle = np.clip(cosine_angle, -1, 1)
            
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)
        except:
            return None
    
    def get_arm_keypoints(self, keypoints):
        """Get keypoints for the active arm"""
        try:
            if self.active_arm == "right":
                shoulder = keypoints[self.POSE_KEYPOINTS['right_shoulder']]
                elbow = keypoints[self.POSE_KEYPOINTS['right_elbow']]
                wrist = keypoints[self.POSE_KEYPOINTS['right_wrist']]
            else:
                shoulder = keypoints[self.POSE_KEYPOINTS['left_shoulder']]
                elbow = keypoints[self.POSE_KEYPOINTS['left_elbow']]
                wrist = keypoints[self.POSE_KEYPOINTS['left_wrist']]
            
            # Check confidence scores
            if all(point[2] > 0.5 for point in [shoulder, elbow, wrist]):
                return shoulder, elbow, wrist
            return None, None, None
        except:
            return None, None, None
    
    def analyze_range_of_motion(self, angles):
        """Analyze range of motion quality"""
        if len(angles) < 2:
            return "insufficient_data", 0
        
        min_angle = min(angles)
        max_angle = max(angles)
        rom_range = max_angle - min_angle
        
        # Determine ROM quality
        for quality, thresholds in self.ROM_THRESHOLDS.items():
            if (min_angle <= thresholds['min'] and 
                max_angle >= thresholds['max']):
                rom_score = min(100, (rom_range / 140) * 100)  # 140° is ideal ROM
                return quality, rom_score
        
        return "poor", max(0, (rom_range / 140) * 100)
    
    def calculate_movement_smoothness(self, angles):
        """Calculate smoothness of movement based on angle changes"""
        if len(angles) < 3:
            return 0
        
        # Calculate second derivative (acceleration) to measure smoothness
        accelerations = []
        for i in range(2, len(angles)):
            acc = angles[i] - 2*angles[i-1] + angles[i-2]
            accelerations.append(abs(acc))
        
        if not accelerations:
            return 0
        
        # Lower acceleration variance = smoother movement
        smoothness = max(0, 100 - np.std(accelerations) * 2)
        return smoothness
    
    def analyze_elbow_stability(self, elbow_positions):
        """Analyze how stable the elbow position is during the movement"""
        if len(elbow_positions) < 5:
            return 0
        
        # Calculate variance in elbow X position (forward/backward movement)
        x_positions = [pos[0] for pos in elbow_positions]
        x_variance = np.var(x_positions)
        
        # Convert variance to stability score (lower variance = higher stability)
        stability_score = max(0, 100 - x_variance / 10)
        return stability_score
    
    def detect_rep_tempo(self, angles):
        """Analyze the tempo and rhythm of the repetition"""
        if len(angles) < 10:
            return "unknown", 0
        
        # Find peaks and valleys to determine concentric/eccentric phases
        peaks = []
        valleys = []
        
        for i in range(1, len(angles) - 1):
            if angles[i] > angles[i-1] and angles[i] > angles[i+1]:
                peaks.append(i)
            elif angles[i] < angles[i-1] and angles[i] < angles[i+1]:
                valleys.append(i)
        
        if len(peaks) > 0 and len(valleys) > 0:
            # Calculate phase durations
            concentric_time = 0
            eccentric_time = 0
            
            # This is a simplified tempo analysis
            total_time = len(angles)
            tempo_score = 100 if 15 <= total_time <= 45 else max(0, 100 - abs(30 - total_time) * 3)
            
            if tempo_score > 80:
                return "good", tempo_score
            elif tempo_score > 60:
                return "moderate", tempo_score
            else:
                return "too_fast" if total_time < 15 else "too_slow", tempo_score
        
        return "irregular", 0
    
    def analyze_bicep_curl_advanced(self, keypoints):
        """Advanced bicep curl analysis with detailed metrics"""
        shoulder, elbow, wrist = self.get_arm_keypoints(keypoints)
        
        if shoulder is None:
            return None, ["❌ Cannot detect arm keypoints clearly"]
        
        # Calculate arm angle
        arm_angle = self.calculate_angle(shoulder, elbow, wrist)
        if arm_angle is None:
            return None, ["❌ Cannot calculate arm angle"]
        
        # Store angle and elbow position
        self.angle_history.append(arm_angle)
        self.elbow_position_history.append([elbow[0], elbow[1]])
        
        # Rep detection logic (optimized for side view)
        feedback = []
        rep_completed = False
        
        # Filter out invalid angles
        if arm_angle < self.ANGLE_THRESHOLDS['min_valid'] or arm_angle > self.ANGLE_THRESHOLDS['max_valid']:
            feedback.append("⚠️  Move closer or adjust position for better detection")
            return feedback, rep_completed
        
        if arm_angle > self.ANGLE_THRESHOLDS['extended']:  # Extended position (160°)
            if self.stage == "up":
                # Rep completed - analyze the full rep
                rep_completed = True
                self.rep_count += 1
                
                # Analyze the completed rep
                rep_analysis = self.analyze_completed_rep()
                feedback.extend(rep_analysis)
                
            self.stage = "down"
            self.current_rep_start = len(self.angle_history) - 1
            self.current_rep_angles = [arm_angle]
            
        elif arm_angle < self.ANGLE_THRESHOLDS['contracted']:  # Flexed position (50°)
            self.stage = "up"
            if self.current_rep_angles:
                self.current_rep_angles.append(arm_angle)
        else:
            # Middle range
            if self.current_rep_angles:
                self.current_rep_angles.append(arm_angle)
        
        # Real-time form feedback
        form_feedback = self.provide_realtime_feedback(arm_angle, elbow)
        feedback.extend(form_feedback)
        
        # Calculate current metrics
        self.update_movement_metrics()
        
        return arm_angle, feedback
    
    def analyze_completed_rep(self):
        """Analyze a completed repetition for detailed feedback"""
        if len(self.current_rep_angles) < 5:
            return ["⚠️ Rep too fast - slow down for better form"]
        
        feedback = []
        
        # Range of Motion Analysis
        rom_quality, rom_score = self.analyze_range_of_motion(self.current_rep_angles)
        if rom_quality == "excellent":
            feedback.append("🎯 Excellent range of motion!")
        elif rom_quality == "good":
            feedback.append("✅ Good range of motion")
        elif rom_quality == "fair":
            feedback.append("⚠️ Try to extend your range of motion")
        else:
            feedback.append("❌ Poor range of motion - go deeper")
        
        # Movement Smoothness
        smoothness = self.calculate_movement_smoothness(self.current_rep_angles)
        if smoothness > 80:
            feedback.append("✅ Smooth, controlled movement")
        elif smoothness > 60:
            feedback.append("⚠️ Movement slightly jerky")
        else:
            feedback.append("❌ Too jerky - focus on control")
        
        # Tempo Analysis
        tempo_quality, tempo_score = self.detect_rep_tempo(self.current_rep_angles)
        if tempo_quality == "good":
            feedback.append("✅ Good tempo")
        elif tempo_quality == "too_fast":
            feedback.append("⚠️ Slow down your reps")
        elif tempo_quality == "too_slow":
            feedback.append("⚠️ Speed up slightly")
        
        # Store rep data for analysis
        rep_data = {
            'rep_number': self.rep_count,
            'angles': self.current_rep_angles.copy(),
            'rom_quality': rom_quality,
            'rom_score': rom_score,
            'smoothness': smoothness,
            'tempo_quality': tempo_quality,
            'tempo_score': tempo_score,
            'timestamp': datetime.now().isoformat()
        }
        self.rep_data.append(rep_data)
        
        return feedback
    
    def provide_realtime_feedback(self, arm_angle, elbow):
        """Provide real-time form feedback"""
        feedback = []
        
        # Angle-specific feedback
        if arm_angle < 20:
            feedback.append("⚠️ Don't curl too high - ease up!")
        elif arm_angle > 180:
            feedback.append("⚠️ Extend your arm more")
        
        # Elbow position feedback
        if len(self.elbow_position_history) > 5:
            recent_positions = list(self.elbow_position_history)[-5:]
            x_variance = np.var([pos[0] for pos in recent_positions])
            
            if x_variance > 100:  # Elbow moving too much
                feedback.append("⚠️ Keep your elbow stable!")
        
        return feedback
    
    def update_movement_metrics(self):
        """Update real-time movement quality metrics"""
        if len(self.angle_history) > 10:
            recent_angles = list(self.angle_history)[-10:]
            self.movement_smoothness = self.calculate_movement_smoothness(recent_angles)
        
        if len(self.elbow_position_history) > 5:
            self.elbow_stability_score = self.analyze_elbow_stability(
                list(self.elbow_position_history)[-5:]
            )
        
        # Calculate overall form score
        self.form_score = (self.movement_smoothness + self.elbow_stability_score) / 2
    
    def draw_advanced_pose_info(self, frame, keypoints, arm_angle):
        """Draw detailed pose information"""
        shoulder, elbow, wrist = self.get_arm_keypoints(keypoints)
        
        if shoulder is None:
            return
        
        # Draw arm connections with thickness based on quality
        thickness = 3 if self.form_score > 70 else 2
        color = (0, 255, 0) if self.form_score > 70 else (0, 255, 255)
        
        cv2.line(frame, (int(shoulder[0]), int(shoulder[1])), 
                (int(elbow[0]), int(elbow[1])), color, thickness)
        cv2.line(frame, (int(elbow[0]), int(elbow[1])), 
                (int(wrist[0]), int(wrist[1])), color, thickness)
        
        # Draw keypoints
        cv2.circle(frame, (int(shoulder[0]), int(shoulder[1])), 8, (255, 0, 0), -1)
        cv2.circle(frame, (int(elbow[0]), int(elbow[1])), 10, (0, 0, 255), -1)
        cv2.circle(frame, (int(wrist[0]), int(wrist[1])), 8, (255, 0, 0), -1)
        
        # Draw angle arc
        if arm_angle:
            self.draw_angle_arc(frame, shoulder, elbow, wrist, arm_angle)
    
    def draw_angle_arc(self, frame, shoulder, elbow, wrist, angle):
        """Draw an arc showing the current angle"""
        try:
            # Calculate arc parameters
            center = (int(elbow[0]), int(elbow[1]))
            
            # Calculate vectors
            vec1 = np.array([shoulder[0] - elbow[0], shoulder[1] - elbow[1]])
            vec2 = np.array([wrist[0] - elbow[0], wrist[1] - elbow[1]])
            
            # Calculate start and end angles for arc
            start_angle = math.degrees(math.atan2(vec1[1], vec1[0]))
            end_angle = math.degrees(math.atan2(vec2[1], vec2[0]))
            
            # Draw arc
            cv2.ellipse(frame, center, (30, 30), 0, start_angle, end_angle, (255, 255, 0), 2)
            
            # Draw angle text
            text_x = center[0] + 40
            text_y = center[1] - 20
            cv2.putText(frame, f'{angle:.1f}°', (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        except:
            pass
    
    def draw_advanced_ui(self, frame, arm_angle):
        """Draw comprehensive UI with advanced metrics"""
        height, width = frame.shape[:2]
        
        # Main info panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, 280), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Title
        cv2.putText(frame, 'Advanced Bicep Curl Tracker', 
                   (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Basic stats
        cv2.putText(frame, f'Reps: {self.rep_count}', 
                   (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        stage_color = (0, 255, 255) if self.stage == "up" else (255, 255, 0)
        cv2.putText(frame, f'Stage: {self.stage.upper()}', 
                   (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, stage_color, 2)
        
        cv2.putText(frame, f'Arm: {self.active_arm.upper()}', 
                   (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Current angle
        if arm_angle:
            angle_color = (0, 255, 0) if 40 <= arm_angle <= 160 else (0, 165, 255)
            cv2.putText(frame, f'Angle: {arm_angle:.1f}°', 
                       (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, angle_color, 2)
        
        # Advanced metrics
        cv2.putText(frame, f'Form Score: {self.form_score:.0f}%', 
                   (20, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   (0, 255, 0) if self.form_score > 70 else (0, 165, 255), 2)
        
        cv2.putText(frame, f'Smoothness: {self.movement_smoothness:.0f}%', 
                   (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f'Elbow Stability: {self.elbow_stability_score:.0f}%', 
                   (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Feedback messages
        feedback_y = 250
        for i, message in enumerate(self.feedback_messages[-2:]):  # Show last 2 messages
            cv2.putText(frame, message, (20, feedback_y + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Range of motion visualization
        self.draw_rom_meter(frame, width - 200, 50)
        
        # Controls
        cv2.putText(frame, "Controls: 'q'-quit 'r'-reset 's'-switch arm", 
                   (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, "'a'-analytics 'e'-export data", 
                   (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    def draw_rom_meter(self, frame, x, y):
        """Draw range of motion meter"""
        if len(self.angle_history) < 2:
            return
        
        recent_angles = list(self.angle_history)[-20:]  # Last 20 measurements
        min_angle = min(recent_angles)
        max_angle = max(recent_angles)
        current_range = max_angle - min_angle
        
        # Draw meter background
        cv2.rectangle(frame, (x, y), (x + 150, y + 80), (50, 50, 50), -1)
        cv2.putText(frame, 'Range of Motion', (x + 10, y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Draw range bar
        bar_width = int((current_range / 140) * 130)  # 140° is ideal ROM
        bar_color = (0, 255, 0) if current_range > 120 else (0, 165, 255) if current_range > 90 else (0, 0, 255)
        
        cv2.rectangle(frame, (x + 10, y + 30), (x + 10 + bar_width, y + 50), bar_color, -1)
        cv2.rectangle(frame, (x + 10, y + 30), (x + 140, y + 50), (100, 100, 100), 2)
        
        cv2.putText(frame, f'{current_range:.0f}°', (x + 10, y + 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def export_session_data(self):
        """Export session data to JSON file"""
        session_data = {
            'session_date': datetime.now().isoformat(),
            'total_reps': self.rep_count,
            'active_arm': self.active_arm,
            'rep_data': self.rep_data,
            'session_summary': {
                'avg_form_score': np.mean([rep['rom_score'] for rep in self.rep_data]) if self.rep_data else 0,
                'avg_smoothness': np.mean([rep['smoothness'] for rep in self.rep_data]) if self.rep_data else 0,
                'total_time': len(self.rep_data) * 30 if self.rep_data else 0  # Approximate
            }
        }
        
        filename = f"bicep_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"Session data exported to {filename}")
        return filename
    
    def show_analytics(self):
        """Display analytics for the current session"""
        if not self.rep_data:
            print("No rep data available for analytics")
            return
        
        print("\n" + "="*50)
        print("BICEP CURL SESSION ANALYTICS")
        print("="*50)
        print(f"Total Reps: {self.rep_count}")
        print(f"Active Arm: {self.active_arm}")
        print(f"Session Duration: ~{len(self.rep_data) * 30} seconds")
        
        # Calculate averages
        rom_scores = [rep['rom_score'] for rep in self.rep_data]
        smoothness_scores = [rep['smoothness'] for rep in self.rep_data]
        
        print(f"\nAverage ROM Score: {np.mean(rom_scores):.1f}%")
        print(f"Average Smoothness: {np.mean(smoothness_scores):.1f}%")
        print(f"Best Rep ROM: {max(rom_scores):.1f}%")
        print(f"Most Smooth Rep: {max(smoothness_scores):.1f}%")
        
        # ROM Quality distribution
        rom_qualities = [rep['rom_quality'] for rep in self.rep_data]
        from collections import Counter
        quality_dist = Counter(rom_qualities)
        
        print(f"\nROM Quality Distribution:")
        for quality, count in quality_dist.items():
            print(f"  {quality.title()}: {count} reps")
        
        print("="*50 + "\n")
    
    def run_advanced_tracking(self):
        """Run the advanced bicep curl tracking system"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Advanced Bicep Curl Tracker Started!")
        print("")
        print("📐 POSITIONING INSTRUCTIONS:")
        print("  🎯 Stand sideways to the camera (90° profile view)")
        print("  📏 Keep your working arm facing the camera")
        print("  🚶 Stand 3-4 feet from camera for best detection")
        print("  💡 Ensure good lighting on your side profile")
        print("  📱 Camera should capture your full upper body")
        print("")
        print("Controls:")
        print("  'q' - Quit")
        print("  'r' - Reset rep count")
        print("  's' - Switch arm (left/right)")
        print("  'a' - Show analytics")
        print("  'e' - Export session data")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            
            # Run pose estimation
            results = self.model(frame, conf=0.5, verbose=False)
            
            if results[0].keypoints is not None and len(results[0].keypoints.data) > 0:
                keypoints = results[0].keypoints.data[0].cpu().numpy()
                
                # Advanced bicep curl analysis
                arm_angle, feedback = self.analyze_bicep_curl_advanced(keypoints)
                
                # Draw advanced pose information
                self.draw_advanced_pose_info(frame, keypoints, arm_angle)
                
                self.feedback_messages = feedback[-3:]  # Keep last 3 messages
            else:
                self.feedback_messages = ["❌ No person detected"]
                arm_angle = None
            
            # Draw advanced UI
            self.draw_advanced_ui(frame, arm_angle)
            
            cv2.imshow('Advanced Bicep Curl Tracker', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.rep_count = 0
                self.rep_data = []
                self.angle_history.clear()
                self.elbow_position_history.clear()
                print("Session reset!")
            elif key == ord('s'):
                self.active_arm = "left" if self.active_arm == "right" else "right"
                print(f"Switched to {self.active_arm} arm")
            elif key == ord('a'):
                self.show_analytics()
            elif key == ord('e'):
                self.export_session_data()
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Final analytics
        if self.rep_data:
            print("\nSession completed!")
            self.show_analytics()

if __name__ == "__main__":
    tracker = AdvancedBicepTracker()
    tracker.run_advanced_tracking()