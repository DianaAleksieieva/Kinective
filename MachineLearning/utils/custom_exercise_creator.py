#!/usr/bin/env python3
"""
Custom Exercise Creator
Allows users to create and train custom exercise patterns
"""

import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import cv2
import time
from datetime import datetime

@dataclass
class KeypointFrame:
    timestamp: float
    keypoints: List[Tuple[float, float, float]]  # x, y, confidence
    frame_number: int

@dataclass
class ExercisePattern:
    name: str
    description: str
    target_keypoints: List[int]  # Indices of important keypoints
    phase_definitions: Dict[str, str]  # phase_name: description
    angle_calculations: List[Dict]  # Angle calculation rules
    rep_detection_rules: Dict  # Rules for detecting reps
    form_scoring_weights: Dict  # Weights for different form aspects
    created_date: str
    training_data: List[KeypointFrame]

class CustomExerciseCreator:
    def __init__(self):
        self.current_pattern = None
        self.recording_data = []
        self.is_recording = False
        self.frame_count = 0
        
        # Keypoint names for reference
        self.keypoint_names = [
            "nose", "left_eye", "right_eye", "left_ear", "right_ear",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ]
    
    def start_new_exercise(self, name: str, description: str) -> None:
        """Start creating a new exercise pattern"""
        print(f"🎨 Creating new exercise: {name}")
        print(f"📝 Description: {description}")
        
        self.current_pattern = ExercisePattern(
            name=name,
            description=description,
            target_keypoints=[],
            phase_definitions={},
            angle_calculations=[],
            rep_detection_rules={},
            form_scoring_weights={},
            created_date=datetime.now().isoformat(),
            training_data=[]
        )
        
        self.recording_data = []
        self.frame_count = 0
        
        print("✅ Exercise template created!")
        self._show_keypoint_reference()
    
    def _show_keypoint_reference(self):
        """Show keypoint indices for user reference"""
        print("\n🔍 KEYPOINT REFERENCE:")
        print("="*30)
        for i, name in enumerate(self.keypoint_names):
            print(f"  {i:2d}: {name}")
        print()
    
    def define_target_keypoints(self, keypoint_indices: List[int]) -> None:
        """Define which keypoints are important for this exercise"""
        if not self.current_pattern:
            print("❌ No exercise pattern active. Start a new exercise first.")
            return
        
        self.current_pattern.target_keypoints = keypoint_indices
        print(f"🎯 Target keypoints set: {[self.keypoint_names[i] for i in keypoint_indices]}")
    
    def define_exercise_phases(self, phases: Dict[str, str]) -> None:
        """Define the phases of the exercise"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        self.current_pattern.phase_definitions = phases
        print("📋 Exercise phases defined:")
        for phase, description in phases.items():
            print(f"  • {phase}: {description}")
    
    def add_angle_calculation(self, name: str, point1: int, point2: int, point3: int, 
                            description: str = "") -> None:
        """Add an angle calculation rule"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        angle_rule = {
            "name": name,
            "point1": point1,
            "point2": point2,  # Vertex of angle
            "point3": point3,
            "description": description
        }
        
        self.current_pattern.angle_calculations.append(angle_rule)
        
        point_names = [self.keypoint_names[i] for i in [point1, point2, point3]]
        print(f"📐 Added angle calculation: {name}")
        print(f"    Points: {point_names[0]} → {point_names[1]} → {point_names[2]}")
    
    def start_recording_demonstration(self) -> None:
        """Start recording demonstration data"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        self.is_recording = True
        self.recording_data = []
        self.frame_count = 0
        print("🔴 Recording demonstration... Perform the exercise slowly and clearly.")
        print("   Press 'q' to stop recording")
    
    def record_frame(self, keypoints: List[Tuple[float, float, float]]) -> None:
        """Record a frame of keypoint data"""
        if not self.is_recording:
            return
        
        frame_data = KeypointFrame(
            timestamp=time.time(),
            keypoints=keypoints,
            frame_number=self.frame_count
        )
        
        self.recording_data.append(frame_data)
        self.frame_count += 1
        
        # Show recording progress
        if self.frame_count % 30 == 0:  # Every second at 30fps
            print(f"📹 Recording... {self.frame_count} frames captured")
    
    def stop_recording_demonstration(self) -> None:
        """Stop recording and analyze the demonstration"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if len(self.recording_data) < 30:  # Less than 1 second
            print("⚠️  Recording too short. Please record at least 1 second of movement.")
            return
        
        self.current_pattern.training_data = self.recording_data
        print(f"✅ Recording complete! Captured {len(self.recording_data)} frames")
        
        # Analyze the demonstration
        self._analyze_demonstration()
    
    def _analyze_demonstration(self) -> None:
        """Analyze recorded demonstration to suggest rep detection rules"""
        if not self.current_pattern.training_data:
            return
        
        print("\n🔍 ANALYZING DEMONSTRATION...")
        print("="*35)
        
        # Calculate angles over time for each defined angle
        for angle_def in self.current_pattern.angle_calculations:
            angles = []
            valid_frames = 0
            
            for frame in self.current_pattern.training_data:
                angle = self._calculate_angle(
                    frame.keypoints[angle_def["point1"]],
                    frame.keypoints[angle_def["point2"]],
                    frame.keypoints[angle_def["point3"]]
                )
                
                if angle is not None:
                    angles.append(angle)
                    valid_frames += 1
            
            if angles:
                min_angle = min(angles)
                max_angle = max(angles)
                avg_angle = np.mean(angles)
                
                print(f"📐 {angle_def['name']}:")
                print(f"    Range: {min_angle:.1f}° - {max_angle:.1f}°")
                print(f"    Average: {avg_angle:.1f}°")
                print(f"    Valid frames: {valid_frames}/{len(self.current_pattern.training_data)}")
                
                # Suggest rep detection thresholds
                if max_angle - min_angle > 30:  # Significant range of motion
                    suggested_rules = {
                        "angle_name": angle_def["name"],
                        "min_threshold": min_angle + 10,
                        "max_threshold": max_angle - 10,
                        "detection_method": "peak_valley"
                    }
                    
                    print(f"💡 Suggested rep detection:")
                    print(f"    Min threshold: {suggested_rules['min_threshold']:.1f}°")
                    print(f"    Max threshold: {suggested_rules['max_threshold']:.1f}°")
        
        # Detect potential rep cycles
        self._detect_rep_patterns()
    
    def _calculate_angle(self, p1: Tuple, p2: Tuple, p3: Tuple) -> Optional[float]:
        """Calculate angle between three points"""
        try:
            x1, y1, conf1 = p1
            x2, y2, conf2 = p2
            x3, y3, conf3 = p3
            
            # Check confidence
            if min(conf1, conf2, conf3) < 0.5:
                return None
            
            # Calculate vectors
            v1 = np.array([x1 - x2, y1 - y2])
            v2 = np.array([x3 - x2, y3 - y2])
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.degrees(np.arccos(cos_angle))
            
            return angle
        except:
            return None
    
    def _detect_rep_patterns(self) -> None:
        """Detect repetitive patterns in the demonstration"""
        if not self.current_pattern.angle_calculations:
            return
        
        print("\n🔄 DETECTING REP PATTERNS...")
        
        # Use the first angle calculation for pattern detection
        angle_def = self.current_pattern.angle_calculations[0]
        angles = []
        
        for frame in self.current_pattern.training_data:
            angle = self._calculate_angle(
                frame.keypoints[angle_def["point1"]],
                frame.keypoints[angle_def["point2"]],
                frame.keypoints[angle_def["point3"]]
            )
            if angle is not None:
                angles.append(angle)
        
        if len(angles) < 30:
            print("⚠️  Not enough valid angle data for pattern detection")
            return
        
        # Simple peak detection
        angles = np.array(angles)
        smoothed = np.convolve(angles, np.ones(5)/5, mode='same')  # Smooth data
        
        # Find peaks and valleys
        peaks = []
        valleys = []
        
        for i in range(1, len(smoothed) - 1):
            if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1]:
                peaks.append((i, smoothed[i]))
            elif smoothed[i] < smoothed[i-1] and smoothed[i] < smoothed[i+1]:
                valleys.append((i, smoothed[i]))
        
        print(f"📊 Found {len(peaks)} peaks and {len(valleys)} valleys")
        
        if len(peaks) >= 2 or len(valleys) >= 2:
            estimated_reps = max(len(peaks), len(valleys))
            print(f"🎯 Estimated reps in demonstration: {estimated_reps}")
            
            # Calculate average rep duration
            if len(peaks) >= 2:
                peak_intervals = [peaks[i+1][0] - peaks[i][0] for i in range(len(peaks)-1)]
                avg_interval = np.mean(peak_intervals)
                frame_rate = 30  # Assuming 30fps
                rep_duration = avg_interval / frame_rate
                print(f"⏱️  Average rep duration: {rep_duration:.1f} seconds")
    
    def set_rep_detection_rules(self, rules: Dict) -> None:
        """Manually set rep detection rules"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        self.current_pattern.rep_detection_rules = rules
        print("✅ Rep detection rules set:")
        for key, value in rules.items():
            print(f"  {key}: {value}")
    
    def set_form_scoring_weights(self, weights: Dict) -> None:
        """Set weights for different aspects of form scoring"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            normalized_weights = {k: v/total for k, v in weights.items()}
            self.current_pattern.form_scoring_weights = normalized_weights
            
            print("⚖️  Form scoring weights set:")
            for aspect, weight in normalized_weights.items():
                print(f"  {aspect}: {weight:.2f}")
    
    def save_custom_exercise(self, filename: Optional[str] = None) -> str:
        """Save the custom exercise pattern"""
        if not self.current_pattern:
            print("❌ No exercise pattern to save.")
            return ""
        
        if not filename:
            filename = f"custom_{self.current_pattern.name.lower().replace(' ', '_')}.json"
        
        # Convert to dictionary for JSON serialization
        pattern_dict = asdict(self.current_pattern)
        
        # Convert training data to serializable format
        pattern_dict["training_data"] = [
            {
                "timestamp": frame.timestamp,
                "keypoints": frame.keypoints,
                "frame_number": frame.frame_number
            }
            for frame in self.current_pattern.training_data
        ]
        
        with open(filename, 'w') as f:
            json.dump(pattern_dict, f, indent=2)
        
        print(f"💾 Custom exercise saved as {filename}")
        return filename
    
    def load_custom_exercise(self, filename: str) -> bool:
        """Load a custom exercise pattern"""
        try:
            with open(filename, 'r') as f:
                pattern_dict = json.load(f)
            
            # Convert training data back to KeypointFrame objects
            training_data = [
                KeypointFrame(
                    timestamp=frame["timestamp"],
                    keypoints=frame["keypoints"],
                    frame_number=frame["frame_number"]
                )
                for frame in pattern_dict.get("training_data", [])
            ]
            
            self.current_pattern = ExercisePattern(
                name=pattern_dict["name"],
                description=pattern_dict["description"],
                target_keypoints=pattern_dict["target_keypoints"],
                phase_definitions=pattern_dict["phase_definitions"],
                angle_calculations=pattern_dict["angle_calculations"],
                rep_detection_rules=pattern_dict["rep_detection_rules"],
                form_scoring_weights=pattern_dict["form_scoring_weights"],
                created_date=pattern_dict["created_date"],
                training_data=training_data
            )
            
            print(f"📂 Loaded custom exercise: {self.current_pattern.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading exercise: {e}")
            return False
    
    def preview_exercise_summary(self) -> None:
        """Show a summary of the current exercise pattern"""
        if not self.current_pattern:
            print("❌ No exercise pattern active.")
            return
        
        print(f"\n📋 EXERCISE SUMMARY: {self.current_pattern.name}")
        print("="*50)
        print(f"Description: {self.current_pattern.description}")
        print(f"Created: {self.current_pattern.created_date}")
        print(f"Target keypoints: {len(self.current_pattern.target_keypoints)}")
        print(f"Angle calculations: {len(self.current_pattern.angle_calculations)}")
        print(f"Training frames: {len(self.current_pattern.training_data)}")
        
        if self.current_pattern.phase_definitions:
            print("\nPhases:")
            for phase, desc in self.current_pattern.phase_definitions.items():
                print(f"  • {phase}: {desc}")
        
        if self.current_pattern.angle_calculations:
            print("\nAngle calculations:")
            for calc in self.current_pattern.angle_calculations:
                print(f"  • {calc['name']}: {calc.get('description', 'No description')}")

# Example usage
if __name__ == "__main__":
    creator = CustomExerciseCreator()
    
    print("🎨 Custom Exercise Creator")
    print("Example: Creating a Shoulder Raise exercise")
    print()
    
    # Create new exercise
    creator.start_new_exercise("Lateral Shoulder Raise", "Raising arms to shoulder level")
    
    # Define target keypoints (shoulders, elbows, wrists)
    creator.define_target_keypoints([5, 6, 7, 8, 9, 10])
    
    # Define phases
    phases = {
        "start": "Arms at sides",
        "raise": "Lifting arms to shoulder level",
        "hold": "Arms parallel to ground",
        "lower": "Returning to start position"
    }
    creator.define_exercise_phases(phases)
    
    # Add angle calculations
    creator.add_angle_calculation("left_arm_angle", 5, 7, 9, "Left arm angle from shoulder")
    creator.add_angle_calculation("right_arm_angle", 6, 8, 10, "Right arm angle from shoulder")
    
    # Set rep detection rules
    rep_rules = {
        "method": "angle_threshold",
        "angle_name": "left_arm_angle",
        "min_angle": 15,
        "max_angle": 85,
        "hold_time": 0.5
    }
    creator.set_rep_detection_rules(rep_rules)
    
    # Set form scoring weights
    form_weights = {
        "symmetry": 0.3,
        "range_of_motion": 0.4,
        "speed_control": 0.3
    }
    creator.set_form_scoring_weights(form_weights)
    
    # Preview and save
    creator.preview_exercise_summary()
    creator.save_custom_exercise()