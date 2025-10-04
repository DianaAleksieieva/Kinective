#!/usr/bin/env python3
"""
Better Audio Sounds for Exercise Tracking
Test different sound options for rep counting
"""

import winsound
import time

def test_sound_options():
    """Test different sound options for rep counting"""
    print("🎵 TESTING BETTER REP COUNTING SOUNDS")
    print("=" * 45)
    print("Listen to each option and see which you prefer...")
    print()
    
    # Option 1: Soft low tone
    print("🔊 Option 1: Soft Low Tone (600Hz)")
    winsound.Beep(600, 300)
    time.sleep(1.5)
    
    # Option 2: Medium pleasant tone
    print("🔊 Option 2: Pleasant Medium Tone (800Hz)")
    winsound.Beep(800, 250)
    time.sleep(1.5)
    
    # Option 3: Warm tone
    print("🔊 Option 3: Warm Tone (700Hz)")
    winsound.Beep(700, 280)
    time.sleep(1.5)
    
    # Option 4: Double soft beep
    print("🔊 Option 4: Double Soft Beep")
    winsound.Beep(650, 150)
    time.sleep(0.1)
    winsound.Beep(650, 150)
    time.sleep(1.5)
    
    # Option 5: Gentle rising tone
    print("🔊 Option 5: Gentle Rising Tone")
    winsound.Beep(600, 150)
    time.sleep(0.05)
    winsound.Beep(700, 150)
    time.sleep(1.5)
    
    # Option 6: Bass thump (very low)
    print("🔊 Option 6: Bass Thump (400Hz)")
    winsound.Beep(400, 200)
    time.sleep(1.5)
    
    # Option 7: Soft notification (like phone)
    print("🔊 Option 7: Soft Notification")
    winsound.Beep(750, 100)
    time.sleep(0.1)
    winsound.Beep(600, 200)
    time.sleep(1.5)
    
    # Option 8: Drum-like (short and punchy)
    print("🔊 Option 8: Drum-like Sound")
    winsound.Beep(500, 100)
    time.sleep(1.5)
    
    print("\n🎯 MILESTONE SOUNDS:")
    print()
    
    # Milestone option 1: Gentle success
    print("🏆 Milestone 1: Gentle Success")
    winsound.Beep(600, 150)
    time.sleep(0.1)
    winsound.Beep(700, 150)
    time.sleep(0.1)
    winsound.Beep(800, 200)
    time.sleep(2)
    
    # Milestone option 2: Achievement chord
    print("🏆 Milestone 2: Achievement Chord")
    winsound.Beep(523, 200)  # C
    time.sleep(0.05)
    winsound.Beep(659, 200)  # E
    time.sleep(0.05)
    winsound.Beep(784, 300)  # G
    time.sleep(2)
    
    print("✅ Sound test complete!")
    print()
    print("💡 Which option did you prefer?")
    print("   I recommend Option 3 (Warm Tone) or Option 7 (Soft Notification)")

def demo_workout_sounds():
    """Demo what a workout would sound like"""
    print("\n🏋️ WORKOUT DEMO")
    print("=" * 20)
    print("Simulating 5 reps with recommended sounds...")
    
    # Session start
    print("🚀 Starting workout...")
    winsound.Beep(500, 100)
    winsound.Beep(600, 100)
    winsound.Beep(700, 150)
    time.sleep(1)
    
    # 5 reps with soft notification sound
    for i in range(1, 6):
        print(f"  💪 Rep {i}")
        # Soft notification sound (Option 7)
        winsound.Beep(750, 100)
        time.sleep(0.1)
        winsound.Beep(600, 200)
        time.sleep(1.8)  # Rest between reps
    
    # Milestone at 5 reps
    print("  🎯 5 reps milestone!")
    winsound.Beep(600, 150)
    time.sleep(0.1)
    winsound.Beep(700, 150)
    time.sleep(0.1)
    winsound.Beep(800, 200)
    time.sleep(1)
    
    print("✅ Workout demo complete!")

if __name__ == "__main__":
    test_sound_options()
    
    input("\nPress Enter to hear a workout demo...")
    demo_workout_sounds()