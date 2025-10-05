#!/usr/bin/env python3
"""
Simple and Reliable Audio Coach
Uses Windows SAPI for speech and system beeps - guaranteed to work!
"""

import win32com.client
import winsound
import threading
import time
from enum import Enum

class FeedbackType(Enum):
    REP_COMPLETED = "rep_completed"
    GOOD_FORM = "good_form"
    IMPROVE_FORM = "improve_form"
    MILESTONE = "milestone"
    SESSION_START = "session_start"
    SESSION_END = "session_end"

class SimpleAudioCoach:
    def __init__(self):
        """Initialize the simple audio coach"""
        try:
            # Initialize Windows SAPI
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            self.tts_available = True
            print("✅ Windows SAPI initialized")
        except Exception as e:
            print(f"⚠️ SAPI init error: {e}")
            self.tts_available = False
        
        # Sound effects using better, softer tones
        self.sound_effects = {
            FeedbackType.REP_COMPLETED: [(750, 100), (600, 200)],  # Soft notification sound
            FeedbackType.GOOD_FORM: (700, 150),                    # Warm tone
            FeedbackType.IMPROVE_FORM: (500, 250),                 # Lower warning tone
            FeedbackType.MILESTONE: [(600, 150), (700, 150), (800, 200)],  # Gentle rising success
            FeedbackType.SESSION_START: [(500, 100), (600, 100), (700, 150)],  # Rising start
            FeedbackType.SESSION_END: [(800, 200), (700, 200), (600, 250)]    # Gentle descending end
        }
        
        # Voice messages
        self.voice_messages = {
            FeedbackType.REP_COMPLETED: [
                "Great rep!",
                "Nice work!", 
                "Keep it up!",
                "Excellent!",
                "Well done!",
                "Perfect!"
            ],
            FeedbackType.GOOD_FORM: [
                "Perfect form!",
                "Great technique!",
                "Excellent control!",
                "Keep that form!"
            ],
            FeedbackType.IMPROVE_FORM: [
                "Check your form",
                "Focus on technique", 
                "Slow down for better form",
                "Control the movement"
            ],
            FeedbackType.MILESTONE: [
                "Milestone reached!",
                "You're crushing it!",
                "Great progress!",
                "Keep going strong!"
            ]
        }
        
        self.message_index = {feedback_type: 0 for feedback_type in FeedbackType}
        self.last_feedback_time = 0
        self.min_feedback_interval = 1.5  # Minimum seconds between audio feedback
    
    def play_sound_effect(self, feedback_type):
        """Play sound effect for feedback type"""
        def play_sounds():
            try:
                if feedback_type in self.sound_effects:
                    sound = self.sound_effects[feedback_type]
                    
                    if isinstance(sound, list):
                        # Play sequence of beeps
                        for freq, duration in sound:
                            winsound.Beep(freq, duration)
                            time.sleep(0.05)
                    else:
                        # Play single beep
                        freq, duration = sound
                        winsound.Beep(freq, duration)
            except Exception as e:
                print(f"Sound effect error: {e}")
        
        # Play in separate thread to avoid blocking
        threading.Thread(target=play_sounds, daemon=True).start()
    
    def speak_message(self, message):
        """Speak a message using Windows SAPI"""
        if not self.tts_available:
            return
        
        def speak():
            try:
                self.speaker.Speak(message)
            except Exception as e:
                print(f"Speech error: {e}")
        
        # Speak in separate thread
        threading.Thread(target=speak, daemon=True).start()
    
    def give_feedback(self, feedback_type, custom_message=None, use_voice=True, use_sound=True):
        """Give audio feedback"""
        current_time = time.time()
        
        # Throttle feedback to avoid spam
        if current_time - self.last_feedback_time < self.min_feedback_interval:
            return
        
        self.last_feedback_time = current_time
        
        # Play sound effect
        if use_sound:
            self.play_sound_effect(feedback_type)
        
        # Speak message
        if use_voice:
            if custom_message:
                self.speak_message(custom_message)
            elif feedback_type in self.voice_messages:
                messages = self.voice_messages[feedback_type]
                # Cycle through messages
                index = self.message_index[feedback_type]
                message = messages[index % len(messages)]
                self.message_index[feedback_type] = (index + 1) % len(messages)
                self.speak_message(message)
    
    def rep_completed(self, rep_number=None):
        """Audio feedback for completed rep"""
        self.give_feedback(FeedbackType.REP_COMPLETED)
        
        # Special milestone feedback
        if rep_number:
            if rep_number % 10 == 0:  # Every 10 reps
                time.sleep(0.8)  # Brief pause
                self.milestone_reached(rep_number)
            elif rep_number % 5 == 0:  # Every 5 reps
                time.sleep(0.5)
                self.speak_message(f"{rep_number} reps completed!")
    
    def good_form_feedback(self):
        """Audio feedback for good form"""
        self.give_feedback(FeedbackType.GOOD_FORM, use_voice=False)  # Sound only to avoid spam
    
    def form_correction(self, specific_tip=None):
        """Audio feedback for form correction"""
        if specific_tip:
            self.give_feedback(FeedbackType.IMPROVE_FORM, custom_message=specific_tip)
        else:
            self.give_feedback(FeedbackType.IMPROVE_FORM)
    
    def milestone_reached(self, count):
        """Audio feedback for milestones"""
        self.give_feedback(
            FeedbackType.MILESTONE, 
            custom_message=f"Amazing! {count} reps completed!"
        )
    
    def session_started(self, exercise_name):
        """Audio feedback for session start"""
        self.give_feedback(
            FeedbackType.SESSION_START,
            custom_message=f"Let's start your {exercise_name} workout!",
            use_sound=True,
            use_voice=True
        )
    
    def session_ended(self, total_reps, exercise_name):
        """Audio feedback for session end"""
        self.give_feedback(
            FeedbackType.SESSION_END,
            custom_message=f"Workout complete! You finished {total_reps} {exercise_name}. Great job!",
            use_sound=True,
            use_voice=True
        )
    
    def motivational_message(self, message):
        """Speak a custom motivational message"""
        self.speak_message(message)

def test_simple_audio_coach():
    """Test the simple audio coach functionality"""
    print("🎵 TESTING SIMPLE AUDIO COACH")
    print("=" * 35)
    
    coach = SimpleAudioCoach()
    
    print("🏋️ Testing session start...")
    coach.session_started("bicep curls")
    time.sleep(3)
    
    print("💪 Testing rep completion...")
    for i in range(1, 11):
        print(f"  Rep {i}...")
        coach.rep_completed(i)
        time.sleep(1.8)  # Wait between reps
    
    print("📐 Testing form feedback...")
    coach.good_form_feedback()
    time.sleep(1.5)
    
    coach.form_correction("Keep your elbow stable")
    time.sleep(2.5)
    
    print("🎯 Testing custom motivation...")
    coach.motivational_message("You're doing amazing! Keep up the great work!")
    time.sleep(3)
    
    print("🏁 Testing session end...")
    coach.session_ended(10, "bicep curls")
    time.sleep(3)
    
    print("✅ Simple audio coach test complete!")

if __name__ == "__main__":
    test_simple_audio_coach()