#!/usr/bin/env python3
"""
Working Audio Coach for Exercise Tracking
Uses Windows TTS and system sounds for real-time feedback
"""

import pyttsx3
import winsound
import threading
import time
from enum import Enum

class FeedbackType(Enum):
    REP_COMPLETED = "rep_completed"
    GOOD_FORM = "good_form"
    IMPROVE_FORM = "improve_form"
    MILESTONE = "milestone"
    SLOW_DOWN = "slow_down"
    SESSION_START = "session_start"
    SESSION_END = "session_end"

class WorkingAudioCoach:
    def __init__(self):
        """Initialize the working audio coach"""
        try:
            # Initialize text-to-speech engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            self.tts_available = True
            print("✅ Text-to-speech initialized")
        except Exception as e:
            print(f"⚠️ TTS init error: {e}")
            self.tts_available = False
        
        # Sound effects using better, softer tones
        self.sound_effects = {
            FeedbackType.REP_COMPLETED: [(750, 100), (600, 200)],  # Soft notification sound
            FeedbackType.GOOD_FORM: (700, 150),                    # Warm tone
            FeedbackType.IMPROVE_FORM: (500, 250),                 # Lower warning tone  
            FeedbackType.MILESTONE: [(600, 150), (700, 150), (800, 200)],  # Gentle rising success
            FeedbackType.SLOW_DOWN: (450, 300),                    # Deep slow tone
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
                "Well done!"
            ],
            FeedbackType.GOOD_FORM: [
                "Perfect form!",
                "Great technique!",
                "Keep that form!",
                "Excellent control!"
            ],
            FeedbackType.IMPROVE_FORM: [
                "Check your form",
                "Focus on technique",
                "Slow down for better form",
                "Control the movement"
            ],
            FeedbackType.SLOW_DOWN: [
                "Slow down the movement",
                "Control the weight",
                "Focus on tempo"
            ],
            FeedbackType.MILESTONE: [
                "10 reps completed!",
                "Halfway there!",
                "You're crushing it!",
                "Great progress!"
            ],
            FeedbackType.SESSION_START: [
                "Let's get started!",
                "Time to work out!",
                "Ready to train!",
                "Let's do this!"
            ],
            FeedbackType.SESSION_END: [
                "Great workout!",
                "Session complete!",
                "Well done today!",
                "Excellent work!"
            ]
        }
        
        self.message_index = {feedback_type: 0 for feedback_type in FeedbackType}
        self.last_feedback_time = 0
        self.min_feedback_interval = 2.0  # Minimum seconds between audio feedback
    
    def play_sound_effect(self, feedback_type):
        """Play sound effect for feedback type"""
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
    
    def speak_message(self, feedback_type):
        """Speak a voice message"""
        if not self.tts_available:
            return
        
        try:
            messages = self.voice_messages.get(feedback_type, ["Good job!"])
            
            # Cycle through messages to avoid repetition
            index = self.message_index[feedback_type]
            message = messages[index % len(messages)]
            self.message_index[feedback_type] = (index + 1) % len(messages)
            
            # Run TTS in separate thread to avoid blocking
            def speak():
                try:
                    self.tts_engine.say(message)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")
            
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Speech error: {e}")
    
    def give_feedback(self, feedback_type, use_voice=True, use_sound=True):
        """Give audio feedback"""
        current_time = time.time()
        
        # Throttle feedback to avoid spam
        if current_time - self.last_feedback_time < self.min_feedback_interval:
            return
        
        self.last_feedback_time = current_time
        
        # Play sound effect immediately
        if use_sound:
            sound_thread = threading.Thread(
                target=self.play_sound_effect, 
                args=(feedback_type,), 
                daemon=True
            )
            sound_thread.start()
        
        # Speak message (if enabled)
        if use_voice:
            self.speak_message(feedback_type)
    
    def rep_completed(self, rep_number=None):
        """Audio feedback for completed rep"""
        self.give_feedback(FeedbackType.REP_COMPLETED)
        if rep_number and rep_number % 5 == 0:  # Every 5 reps
            time.sleep(0.5)  # Brief pause
            self.milestone_reached(rep_number)
    
    def good_form_feedback(self):
        """Audio feedback for good form"""
        self.give_feedback(FeedbackType.GOOD_FORM, use_voice=False)  # Sound only
    
    def form_correction(self):
        """Audio feedback for form correction"""
        self.give_feedback(FeedbackType.IMPROVE_FORM)
    
    def milestone_reached(self, count):
        """Audio feedback for milestones"""
        self.give_feedback(FeedbackType.MILESTONE)
        # Speak the specific number
        if self.tts_available:
            threading.Thread(
                target=lambda: self.tts_engine.say(f"{count} reps completed!") or self.tts_engine.runAndWait(),
                daemon=True
            ).start()
    
    def session_started(self, exercise_name):
        """Audio feedback for session start"""
        self.give_feedback(FeedbackType.SESSION_START)
        if self.tts_available:
            threading.Thread(
                target=lambda: self.tts_engine.say(f"Starting {exercise_name} tracking") or self.tts_engine.runAndWait(),
                daemon=True
            ).start()
    
    def session_ended(self, total_reps, exercise_name):
        """Audio feedback for session end"""
        self.give_feedback(FeedbackType.SESSION_END)
        if self.tts_available:
            threading.Thread(
                target=lambda: self.tts_engine.say(f"Workout complete! {total_reps} {exercise_name} reps finished!") or self.tts_engine.runAndWait(),
                daemon=True
            ).start()

def test_audio_coach():
    """Test the audio coach functionality"""
    print("🎵 TESTING WORKING AUDIO COACH")
    print("=" * 35)
    
    coach = WorkingAudioCoach()
    
    print("🏋️ Testing session start...")
    coach.session_started("bicep curls")
    time.sleep(2)
    
    print("💪 Testing rep completion...")
    for i in range(1, 6):
        print(f"  Rep {i}...")
        coach.rep_completed(i)
        time.sleep(1.5)
    
    print("📐 Testing form feedback...")
    coach.good_form_feedback()
    time.sleep(1)
    
    coach.form_correction()
    time.sleep(2)
    
    print("🎯 Testing milestone...")
    coach.milestone_reached(10)
    time.sleep(2)
    
    print("🏁 Testing session end...")
    coach.session_ended(10, "bicep curl")
    time.sleep(2)
    
    print("✅ Audio coach test complete!")

if __name__ == "__main__":
    test_audio_coach()