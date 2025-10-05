import cv2
import numpy as np
from ultralytics import YOLO
import math

class ExerciseTracker:
    def __init__(self, model_path="yolo11n-pose.pt"):
        """Initialize the exercise tracker with pose estimation model"""
        self.model = YOLO(model_path)
        
        # COCO pose keypoint indices (from documentation)
        self.POSE_KEYPOINTS = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 5,
            'right_shoulder': 6,
            'left_elbow': 7,
            'right_elbow': 8,
            'left_wrist': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16
        }
        
        # Exercise tracking variables
        self.rep_count = 0
        self.stage = "down"  # "up" or "down"
        self.feedback_messages = []
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        # Convert points to numpy arrays
        a = np.array(point1)  # First point
        b = np.array(point2)  # Middle point (vertex)
        c = np.array(point3)  # Third point
        
        # Calculate vectors
        ba = a - b
        bc = c - b
        
        # Calculate cosine of angle
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        
        # Ensure cosine is in valid range [-1, 1]
        cosine_angle = np.clip(cosine_angle, -1, 1)
        
        # Calculate angle in degrees
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)
    
    def analyze_bicep_curl(self, keypoints):
        """Analyze bicep curl form and count reps"""
        feedback = []
        
        # Get relevant keypoints for right arm (you can modify for left arm)
        try:
            shoulder = keypoints[self.POSE_KEYPOINTS['right_shoulder']]
            elbow = keypoints[self.POSE_KEYPOINTS['right_elbow']]
            wrist = keypoints[self.POSE_KEYPOINTS['right_wrist']]
            
            # Check if all keypoints are detected (confidence > 0.5)
            if all(point[2] > 0.5 for point in [shoulder, elbow, wrist]):
                # Calculate arm angle (shoulder-elbow-wrist)
                arm_angle = self.calculate_angle(
                    [shoulder[0], shoulder[1]], 
                    [elbow[0], elbow[1]], 
                    [wrist[0], wrist[1]]
                )
                
                # Rep counting logic
                if arm_angle > 160:  # Arm extended (down position)
                    if self.stage == "up":
                        self.rep_count += 1
                    self.stage = "down"
                elif arm_angle < 50:  # Arm flexed (up position)
                    self.stage = "up"
                
                # Form feedback
                if arm_angle < 30:
                    feedback.append("⚠️ Too much curl - don't go too high!")
                elif arm_angle > 170:
                    feedback.append("✅ Good extension")
                elif 50 <= arm_angle <= 160:
                    feedback.append("✅ Good range of motion")
                
                # Check elbow position (should stay relatively stable)
                # This is a simplified check - you can make it more sophisticated
                if abs(elbow[0] - shoulder[0]) > 50:  # Elbow moved too far forward/back
                    feedback.append("⚠️ Keep your elbow close to your body!")
                
                return arm_angle, feedback
            else:
                return None, ["❌ Can't detect all arm keypoints clearly"]
                
        except (IndexError, KeyError) as e:
            return None, [f"❌ Error detecting pose: {str(e)}"]
    
    def draw_pose_info(self, frame, keypoints, arm_angle):
        """Draw pose information on the frame"""
        height, width = frame.shape[:2]
        
        # Draw keypoints and connections for the arm
        try:
            shoulder = keypoints[self.POSE_KEYPOINTS['right_shoulder']]
            elbow = keypoints[self.POSE_KEYPOINTS['right_elbow']]
            wrist = keypoints[self.POSE_KEYPOINTS['right_wrist']]
            
            if all(point[2] > 0.5 for point in [shoulder, elbow, wrist]):
                # Draw connections
                cv2.line(frame, 
                        (int(shoulder[0]), int(shoulder[1])), 
                        (int(elbow[0]), int(elbow[1])), 
                        (0, 255, 0), 3)
                cv2.line(frame, 
                        (int(elbow[0]), int(elbow[1])), 
                        (int(wrist[0]), int(wrist[1])), 
                        (0, 255, 0), 3)
                
                # Draw keypoints
                for point in [shoulder, elbow, wrist]:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 8, (0, 0, 255), -1)
                
                # Draw angle text
                if arm_angle:
                    cv2.putText(frame, f'Arm Angle: {arm_angle:.1f}°', 
                              (int(elbow[0]) + 20, int(elbow[1]) - 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        except:
            pass
    
    def run_webcam_tracking(self):
        """Run real-time exercise tracking from webcam"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting exercise tracking...")
        print("Press 'q' to quit, 'r' to reset rep count")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            
            # Run pose estimation
            results = self.model(frame, conf=0.5, verbose=False)
            
            # Process results
            if results[0].keypoints is not None and len(results[0].keypoints.data) > 0:
                keypoints = results[0].keypoints.data[0].cpu().numpy()  # Get first person
                
                # Analyze bicep curl
                arm_angle, feedback = self.analyze_bicep_curl(keypoints)
                
                # Draw pose information
                self.draw_pose_info(frame, keypoints, arm_angle)
                
                # Update feedback messages
                self.feedback_messages = feedback[-3:]  # Keep last 3 messages
            else:
                self.feedback_messages = ["❌ No person detected"]
                arm_angle = None
            
            # Draw UI information
            self.draw_ui(frame, arm_angle)
            
            # Display frame
            cv2.imshow('Exercise Tracker - Bicep Curls', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.rep_count = 0
                print("Rep count reset!")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def draw_ui(self, frame, arm_angle):
        """Draw user interface information on frame"""
        height, width = frame.shape[:2]
        
        # Draw semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (320, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Rep counter
        cv2.putText(frame, f'Reps: {self.rep_count}', 
                   (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Current stage
        stage_color = (0, 255, 255) if self.stage == "up" else (255, 255, 0)
        cv2.putText(frame, f'Stage: {self.stage.upper()}', 
                   (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, stage_color, 2)
        
        # Arm angle
        if arm_angle:
            cv2.putText(frame, f'Angle: {arm_angle:.1f}°', 
                       (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Feedback messages
        y_offset = 170
        for i, message in enumerate(self.feedback_messages):
            cv2.putText(frame, message, 
                       (20, y_offset + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Instructions
        cv2.putText(frame, "Press 'q' to quit, 'r' to reset", 
                   (width - 300, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

if __name__ == "__main__":
    # Create and run exercise tracker
    tracker = ExerciseTracker()
    tracker.run_webcam_tracking()