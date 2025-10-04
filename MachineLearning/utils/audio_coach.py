#!/usr/bin/env python3
"""
Audio Feedback System for Exercise Tracking
Provides real-time audio coaching and feedback
"""

import pygame
import threading
from gtts import gTTS
import io
import os
from enum import Enum

class FeedbackType(Enum):
    REP_COMPLETED = "rep_completed"
    GOOD_FORM = "good_form"
    IMPROVE_FORM = "improve_form"
    SLOW_DOWN = "slow_down"
    SPEED_UP = "speed_up"
    MILESTONE = "milestone"

class AudioCoach:
    def __init__(self):
        pygame.mixer.init()
        self.feedback_messages = {
            FeedbackType.REP_COMPLETED: [
                "Great rep!",
                "Nice work!",
                "Keep it up!",
                "Excellent form!"
            ],
            FeedbackType.GOOD_FORM: [
                "Perfect form!",
                "Great technique!",
                "Keep that form!"
            ],
            FeedbackType.IMPROVE_FORM: [
                "Check your form",
                "Focus on technique",
                "Slow down for better form"
            ],
            FeedbackType.SLOW_DOWN: [
                "Slow down the movement",
                "Control the weight",
                "Focus on tempo"
            ],
            FeedbackType.MILESTONE: [
                "10 reps completed!",
                "Halfway there!",
                "You're crushing it!"
            ]
        }
        
        # Sound effects
        self.load_sound_effects()
        
    def load_sound_effects(self):
        """Load sound effects (you can add .wav files here)"""
        self.sounds = {
            'rep_complete': None,  # pygame.mixer.Sound('rep_complete.wav')
            'milestone': None,     # pygame.mixer.Sound('milestone.wav')
            'warning': None        # pygame.mixer.Sound('warning.wav')
        }
    
    def speak_feedback(self, feedback_type, custom_message=None):
        """Generate and play audio feedback"""
        if custom_message:
            message = custom_message
        else:
            import random
            message = random.choice(self.feedback_messages[feedback_type])
        
        # For now, just print (you can integrate TTS here)
        print(f"🔊 AUDIO: {message}")
        
        # Uncomment below for actual TTS (requires internet)
        # threading.Thread(target=self._play_tts, args=(message,)).start()
    
    def _play_tts(self, text):
        """Play text-to-speech audio"""
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def play_sound_effect(self, sound_name):
        """Play sound effect"""
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

class SmartCoach:
    def __init__(self):
        self.audio_coach = AudioCoach()
        self.rep_count = 0
        self.form_score_history = []
        
    def analyze_performance(self, form_score, rep_completed, tempo_score=None):
        """Analyze performance and provide smart feedback"""
        if rep_completed:
            self.rep_count += 1
            self.form_score_history.append(form_score)
            
            # Rep completed feedback
            if form_score > 90:
                self.audio_coach.speak_feedback(FeedbackType.GOOD_FORM)
            elif form_score < 70:
                self.audio_coach.speak_feedback(FeedbackType.IMPROVE_FORM)
            else:
                self.audio_coach.speak_feedback(FeedbackType.REP_COMPLETED)
            
            # Milestone feedback
            if self.rep_count % 10 == 0:
                self.audio_coach.speak_feedback(
                    FeedbackType.MILESTONE, 
                    f"{self.rep_count} reps completed! Great job!"
                )
        
        # Form guidance
        if len(self.form_score_history) >= 3:
            recent_avg = sum(self.form_score_history[-3:]) / 3
            if recent_avg < 60:
                self.audio_coach.speak_feedback(FeedbackType.IMPROVE_FORM)
    
    def provide_encouragement(self):
        """Provide motivational feedback"""
        encouragements = [
            "You're doing great!",
            "Keep pushing!",
            "Strong work!",
            "You've got this!"
        ]
        import random
        message = random.choice(encouragements)
        self.audio_coach.speak_feedback(FeedbackType.REP_COMPLETED, message)