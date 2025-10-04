#!/usr/bin/env python3
"""
Exercise Selection Menu
Interactive menu for choosing exercises and viewing progress
"""

import cv2
import numpy as np
from typing import Dict, List, Callable
import subprocess
import sys
import os

class ExerciseMenu:
    def __init__(self):
        self.exercises = {
            "1": {
                "name": "💪 Bicep Curls",
                "description": "Track bicep curl form and reps",
                "script": "advanced_bicep_tracker.py",
                "camera_angle": "90° Side View",
                "difficulty": "Beginner"
            },
            "2": {
                "name": "🤲 Push-ups", 
                "description": "Analyze push-up form and depth",
                "script": "advanced_pushup_tracker.py",
                "camera_angle": "45° Diagonal",
                "difficulty": "Beginner"
            },
            "3": {
                "name": "🦵 Squats",
                "description": "Track squat depth and form",
                "script": "advanced_squat_tracker.py", 
                "camera_angle": "Front View",
                "difficulty": "Intermediate"
            },
            "4": {
                "name": "🏃‍♂️ Lunges",
                "description": "Monitor lunge balance and form",
                "script": "advanced_lunge_tracker.py",
                "camera_angle": "Side View", 
                "difficulty": "Intermediate"
            },
            "5": {
                "name": "🏋️ Shoulder Press",
                "description": "Track overhead pressing form",
                "script": "advanced_shoulder_tracker.py",
                "camera_angle": "Front View",
                "difficulty": "Advanced"
            }
        }
        
        self.menu_image = None
        self.create_menu_image()
    
    def create_menu_image(self):
        """Create a visual menu image"""
        # Create a black image
        img_height = 600
        img_width = 800
        self.menu_image = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        
        # Title
        cv2.putText(self.menu_image, "KINECTIVE - AI Exercise Tracker", 
                   (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
        
        cv2.putText(self.menu_image, "Select an Exercise:", 
                   (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Exercise options
        y_start = 150
        for key, exercise in self.exercises.items():
            y_pos = y_start + (int(key) - 1) * 80
            
            # Exercise number and name
            cv2.putText(self.menu_image, f"{key}. {exercise['name']}", 
                       (70, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Description
            cv2.putText(self.menu_image, exercise['description'], 
                       (90, y_pos + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Camera angle and difficulty
            info_text = f"Camera: {exercise['camera_angle']} | {exercise['difficulty']}"
            cv2.putText(self.menu_image, info_text, 
                       (90, y_pos + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # Instructions
        cv2.putText(self.menu_image, "Press number key to select exercise", 
                   (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(self.menu_image, "Press 'q' to quit", 
                   (50, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    def display_menu(self):
        """Display the interactive menu"""
        print("="*60)
        print("🏋️ KINECTIVE - AI Exercise Tracker")
        print("="*60)
        print()
        
        for key, exercise in self.exercises.items():
            print(f"{key}. {exercise['name']}")
            print(f"   📝 {exercise['description']}")
            print(f"   📹 Camera: {exercise['camera_angle']}")
            print(f"   🎯 Difficulty: {exercise['difficulty']}")
            print()
        
        print("0. 📊 View Progress & Stats")
        print("q. ❌ Quit")
        print()
        
        return input("Select an option: ").strip().lower()
    
    def show_camera_setup_guide(self, exercise_key: str):
        """Show camera setup guide for selected exercise"""
        if exercise_key not in self.exercises:
            return
        
        exercise = self.exercises[exercise_key]
        print(f"\n📐 Camera Setup for {exercise['name']}:")
        print(f"📹 Position: {exercise['camera_angle']}")
        
        # Specific setup instructions
        if "Bicep" in exercise['name']:
            print("🎯 Stand sideways to camera (profile view)")
            print("📏 Camera at elbow height")
            print("🚶 Stand 3-4 feet from camera")
        elif "Push-up" in exercise['name']:
            print("🎯 Position camera at 45° diagonal above")
            print("📏 Camera should see your full body")
            print("🚶 Camera 4-5 feet away")
        elif "Squat" in exercise['name']:
            print("🎯 Face the camera directly")
            print("📏 Camera at hip height")
            print("🚶 Stand 4-5 feet from camera")
        
        print("\n💡 General Tips:")
        print("✅ Good, even lighting")
        print("✅ Plain background")
        print("✅ Fitted clothing")
        print("✅ Clear view of movement")
        
        input("\nPress Enter when ready to start...")
    
    def run_exercise(self, exercise_key: str):
        """Run the selected exercise tracker"""
        if exercise_key not in self.exercises:
            print("Invalid exercise selection!")
            return
        
        exercise = self.exercises[exercise_key]
        script_path = exercise['script']
        
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"❌ Exercise script not found: {script_path}")
            print("Available exercises may be limited.")
            return
        
        print(f"\n🚀 Starting {exercise['name']}...")
        
        try:
            # Run the exercise script
            subprocess.run([sys.executable, script_path])
        except KeyboardInterrupt:
            print("\n⏹️  Exercise stopped by user")
        except Exception as e:
            print(f"❌ Error running exercise: {e}")
    
    def show_progress(self):
        """Show user progress and statistics"""
        try:
            from .utils.gamification import GamificationEngine
            
            game_engine = GamificationEngine()
            progress = game_engine.get_progress_summary()
            
            print("\n📊 YOUR PROGRESS")
            print("="*40)
            print(f"🏆 Level: {progress['level']}")
            print(f"💪 Total Reps: {progress['total_reps']}")
            print(f"📅 Sessions: {progress['total_sessions']}")
            print(f"🔥 Current Streak: {progress['current_streak']} days")
            print(f"🏅 Best Streak: {progress['longest_streak']} days")
            print(f"⭐ Best Form Score: {progress['best_form_score']:.1f}%")
            print(f"🎯 Achievements: {progress['achievements_unlocked']}")
            print(f"🎪 Exercises Tried: {progress['exercises_mastered']}")
            
        except ImportError:
            print("📊 Progress tracking not available")
        except Exception as e:
            print(f"Error loading progress: {e}")
    
    def run(self):
        """Run the main menu loop"""
        while True:
            choice = self.display_menu()
            
            if choice == 'q':
                print("👋 Thanks for using Kinective!")
                break
            elif choice == '0':
                self.show_progress()
                input("\nPress Enter to continue...")
            elif choice in self.exercises:
                self.show_camera_setup_guide(choice)
                self.run_exercise(choice)
            else:
                print("❌ Invalid selection. Please try again.")
            
            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    menu = ExerciseMenu()
    menu.run()