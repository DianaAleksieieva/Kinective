#!/usr/bin/env python3
"""
Simple Audio Test for Exercise Tracker
Test audio capabilities without external dependencies
"""

import sys
import platform

def test_basic_audio():
    """Test basic system audio capabilities"""
    print("🔊 AUDIO SYSTEM TEST")
    print("=" * 30)
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    
    # Test 1: Windows built-in beep
    if platform.system() == "Windows":
        try:
            import winsound
            print("\n✅ Windows audio module available")
            
            print("🔔 Testing system beep...")
            winsound.Beep(1000, 500)  # 1000Hz for 500ms
            print("✅ System beep successful!")
            
            print("🎵 Testing different tones...")
            # Success tone (high pitch)
            winsound.Beep(1500, 200)
            winsound.Beep(1200, 200)
            print("✅ Success tone played!")
            
            # Warning tone (lower pitch)
            winsound.Beep(800, 300)
            print("✅ Warning tone played!")
            
            return True
            
        except ImportError:
            print("❌ Windows audio not available")
        except Exception as e:
            print(f"❌ Windows audio error: {e}")
    
    # Test 2: Cross-platform system bell
    try:
        print("\n🔔 Testing system bell...")
        print("\a")  # ASCII bell character
        print("✅ System bell sent (may be silent on some systems)")
    except Exception as e:
        print(f"❌ System bell error: {e}")
    
    return False

def test_pygame_audio():
    """Test pygame audio if available"""
    print("\n🎮 PYGAME AUDIO TEST")
    print("=" * 25)
    
    try:
        import pygame
        print("✅ Pygame available")
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✅ Pygame mixer initialized")
        
        # Test basic sound generation
        import numpy as np
        
        # Generate a simple tone
        duration = 0.5  # seconds
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Success tone (C major chord)
        freq1, freq2, freq3 = 523, 659, 784  # C, E, G
        wave = (np.sin(freq1 * 2 * np.pi * t) + 
                np.sin(freq2 * 2 * np.pi * t) + 
                np.sin(freq3 * 2 * np.pi * t)) / 3
        
        # Convert to pygame sound
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        
        print("🎵 Playing success chord...")
        sound.play()
        pygame.time.wait(int(duration * 1000))
        
        print("✅ Pygame audio test successful!")
        
        pygame.mixer.quit()
        return True
        
    except ImportError as e:
        print(f"❌ Pygame not available: {e}")
        print("💡 Install with: pip install pygame")
    except Exception as e:
        print(f"❌ Pygame audio error: {e}")
    
    return False

def test_text_to_speech():
    """Test text-to-speech capabilities"""
    print("\n🗣️ TEXT-TO-SPEECH TEST")
    print("=" * 25)
    
    # Test Windows SAPI
    if platform.system() == "Windows":
        try:
            import win32com.client
            
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            print("✅ Windows SAPI available")
            
            print("🗣️ Testing speech...")
            speaker.Speak("Exercise tracker audio test successful!")
            
            print("✅ Windows TTS test successful!")
            return True
            
        except ImportError:
            print("❌ Windows SAPI not available")
            print("💡 Install with: pip install pywin32")
        except Exception as e:
            print(f"❌ Windows TTS error: {e}")
    
    # Test pyttsx3 (cross-platform)
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        print("✅ pyttsx3 available")
        
        print("🗣️ Testing speech...")
        engine.say("Audio coaching system ready!")
        engine.runAndWait()
        
        print("✅ pyttsx3 test successful!")
        return True
        
    except ImportError:
        print("❌ pyttsx3 not available")
        print("💡 Install with: pip install pyttsx3")
    except Exception as e:
        print(f"❌ pyttsx3 error: {e}")
    
    # Test gTTS (Google Text-to-Speech)
    try:
        from gtts import gTTS
        import pygame
        import io
        
        print("✅ gTTS available")
        
        # Create speech
        tts = gTTS(text="Great job! Keep up the excellent form!", lang='en')
        
        # Save to memory
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        print("✅ gTTS speech generated")
        print("ℹ️  gTTS requires internet connection for full test")
        return True
        
    except ImportError:
        print("❌ gTTS not available")
        print("💡 Install with: pip install gtts")
    except Exception as e:
        print(f"❌ gTTS error: {e}")
    
    return False

def create_simple_audio_feedback():
    """Create a simple audio feedback system that works without dependencies"""
    print("\n🔧 CREATING SIMPLE AUDIO SYSTEM")
    print("=" * 35)
    
    if platform.system() == "Windows":
        print("💡 Creating Windows-compatible audio feedback...")
        
        audio_code = '''
import winsound
import time

class SimpleAudioCoach:
    def __init__(self):
        self.sounds = {
            "rep_complete": (1200, 200),    # High beep
            "good_form": (1500, 150),       # Higher beep
            "warning": (800, 300),          # Lower beep
            "milestone": [(1000, 100), (1200, 100), (1500, 200)]  # Sequence
        }
    
    def play_sound(self, sound_type):
        """Play audio feedback"""
        try:
            if sound_type in self.sounds:
                sound = self.sounds[sound_type]
                
                if isinstance(sound, list):
                    # Play sequence
                    for freq, duration in sound:
                        winsound.Beep(freq, duration)
                        time.sleep(0.05)
                else:
                    # Play single tone
                    freq, duration = sound
                    winsound.Beep(freq, duration)
                    
        except Exception as e:
            print(f"Audio error: {e}")
    
    def rep_completed(self):
        self.play_sound("rep_complete")
    
    def good_form(self):
        self.play_sound("good_form")
    
    def warning(self):
        self.play_sound("warning")
    
    def milestone(self, reps):
        self.play_sound("milestone")
        print(f"🎯 {reps} reps completed!")

# Test the simple audio coach
if __name__ == "__main__":
    coach = SimpleAudioCoach()
    
    print("Testing simple audio feedback...")
    
    print("🔔 Rep completed sound...")
    coach.rep_completed()
    time.sleep(1)
    
    print("✅ Good form sound...")
    coach.good_form()
    time.sleep(1)
    
    print("⚠️ Warning sound...")
    coach.warning()
    time.sleep(1)
    
    print("🎯 Milestone sound...")
    coach.milestone(10)
    
    print("✅ Simple audio test complete!")
'''
        
        with open("simple_audio_coach.py", "w") as f:
            f.write(audio_code)
        
        print("✅ Created simple_audio_coach.py")
        return True
    
    else:
        print("💡 For non-Windows systems, using print-based feedback...")
        return False

def main():
    """Run all audio tests"""
    print("🎧 EXERCISE TRACKER AUDIO DIAGNOSTICS")
    print("=" * 50)
    
    results = {
        "basic_audio": test_basic_audio(),
        "pygame_audio": test_pygame_audio(),
        "text_to_speech": test_text_to_speech()
    }
    
    print("\n📊 AUDIO TEST RESULTS")
    print("=" * 25)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if any(results.values()):
        print("\n✅ At least one audio system is working!")
    else:
        print("\n⚠️ No audio systems working - creating fallback...")
        create_simple_audio_feedback()
    
    print("\n💡 RECOMMENDATIONS:")
    if not results["pygame_audio"]:
        print("  • Install pygame: pip install pygame")
    if not results["text_to_speech"]:
        print("  • Install pyttsx3: pip install pyttsx3")
        print("  • Or install pywin32: pip install pywin32 (Windows)")
    
    print("\n🎯 For exercise tracking, you can use:")
    print("  • System beeps (minimal but functional)")
    print("  • Visual feedback (always available)")
    print("  • Simple audio coach (Windows)")

if __name__ == "__main__":
    main()