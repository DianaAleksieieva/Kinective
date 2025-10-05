#!/usr/bin/env python3
"""
Gamification System for Exercise Tracking
Achievements, streaks, and progress tracking
"""

import json
import datetime
from dataclasses import dataclass
from typing import List, Dict
import os

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    requirement: int
    unlocked: bool = False
    unlock_date: str = None

@dataclass
class WorkoutSession:
    date: str
    exercise_type: str
    total_reps: int
    avg_form_score: float
    duration_minutes: float
    calories_burned: float

class GamificationEngine:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.data_file = f"user_progress_{user_id}.json"
        
        # Initialize achievements
        self.achievements = self._create_achievements()
        self.user_stats = self._load_user_stats()
        
    def _create_achievements(self) -> List[Achievement]:
        """Create all available achievements"""
        return [
            # Rep-based achievements
            Achievement("first_rep", "First Steps", "Complete your first rep", "🎯", 1),
            Achievement("10_reps", "Getting Started", "Complete 10 reps in a session", "💪", 10),
            Achievement("50_reps", "Strong Foundation", "Complete 50 reps in a session", "🏗️", 50),
            Achievement("100_reps", "Century Club", "Complete 100 reps in a session", "💯", 100),
            
            # Form-based achievements
            Achievement("perfect_form", "Form Master", "Achieve 95%+ form score", "⭐", 95),
            Achievement("consistency", "Consistent Performer", "10 reps with 80%+ form", "🎯", 10),
            
            # Streak achievements
            Achievement("daily_streak_3", "Building Habits", "3 day workout streak", "📅", 3),
            Achievement("daily_streak_7", "Week Warrior", "7 day workout streak", "🔥", 7),
            Achievement("daily_streak_30", "Monthly Machine", "30 day workout streak", "👑", 30),
            
            # Exercise variety
            Achievement("multi_exercise", "Variety Seeker", "Try 3 different exercises", "🎪", 3),
            Achievement("all_exercises", "Exercise Expert", "Master all available exercises", "🏆", 5),
            
            # Performance achievements
            Achievement("speed_demon", "Speed Demon", "Complete 20 RPM", "⚡", 20),
            Achievement("endurance", "Endurance Master", "Workout for 30+ minutes", "⏰", 30),
        ]
    
    def _load_user_stats(self) -> Dict:
        """Load user statistics from file"""
        default_stats = {
            "total_reps": 0,
            "total_sessions": 0,
            "best_form_score": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_workout_date": None,
            "exercises_tried": set(),
            "session_history": [],
            "unlocked_achievements": []
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    loaded_stats = json.load(f)
                    # Convert exercises_tried back to set
                    if 'exercises_tried' in loaded_stats:
                        loaded_stats['exercises_tried'] = set(loaded_stats['exercises_tried'])
                    return {**default_stats, **loaded_stats}
            except:
                return default_stats
        
        return default_stats
    
    def save_user_stats(self):
        """Save user statistics to file"""
        # Convert set to list for JSON serialization
        stats_to_save = self.user_stats.copy()
        stats_to_save['exercises_tried'] = list(stats_to_save['exercises_tried'])
        
        with open(self.data_file, 'w') as f:
            json.dump(stats_to_save, f, indent=2)
    
    def record_session(self, session: WorkoutSession):
        """Record a workout session and check for achievements"""
        # Update stats
        self.user_stats['total_reps'] += session.total_reps
        self.user_stats['total_sessions'] += 1
        self.user_stats['best_form_score'] = max(self.user_stats['best_form_score'], session.avg_form_score)
        self.user_stats['exercises_tried'].add(session.exercise_type)
        self.user_stats['session_history'].append(session.__dict__)
        
        # Update streak
        self._update_streak(session.date)
        
        # Check for new achievements
        new_achievements = self._check_achievements(session)
        
        # Save progress
        self.save_user_stats()
        
        return new_achievements
    
    def _update_streak(self, session_date: str):
        """Update workout streak"""
        today = datetime.datetime.now().date()
        last_workout = None
        
        if self.user_stats['last_workout_date']:
            last_workout = datetime.datetime.strptime(
                self.user_stats['last_workout_date'], '%Y-%m-%d'
            ).date()
        
        if last_workout:
            days_diff = (today - last_workout).days
            if days_diff == 1:  # Consecutive day
                self.user_stats['current_streak'] += 1
            elif days_diff > 1:  # Streak broken
                self.user_stats['current_streak'] = 1
        else:
            self.user_stats['current_streak'] = 1
        
        # Update longest streak
        self.user_stats['longest_streak'] = max(
            self.user_stats['longest_streak'], 
            self.user_stats['current_streak']
        )
        
        self.user_stats['last_workout_date'] = today.strftime('%Y-%m-%d')
    
    def _check_achievements(self, session: WorkoutSession) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        new_achievements = []
        
        for achievement in self.achievements:
            if achievement.id in self.user_stats['unlocked_achievements']:
                continue
            
            unlocked = False
            
            # Rep-based achievements
            if achievement.id == "first_rep" and session.total_reps >= 1:
                unlocked = True
            elif achievement.id == "10_reps" and session.total_reps >= 10:
                unlocked = True
            elif achievement.id == "50_reps" and session.total_reps >= 50:
                unlocked = True
            elif achievement.id == "100_reps" and session.total_reps >= 100:
                unlocked = True
            
            # Form-based achievements
            elif achievement.id == "perfect_form" and session.avg_form_score >= 95:
                unlocked = True
            
            # Streak achievements
            elif achievement.id == "daily_streak_3" and self.user_stats['current_streak'] >= 3:
                unlocked = True
            elif achievement.id == "daily_streak_7" and self.user_stats['current_streak'] >= 7:
                unlocked = True
            elif achievement.id == "daily_streak_30" and self.user_stats['current_streak'] >= 30:
                unlocked = True
            
            # Exercise variety
            elif achievement.id == "multi_exercise" and len(self.user_stats['exercises_tried']) >= 3:
                unlocked = True
            elif achievement.id == "all_exercises" and len(self.user_stats['exercises_tried']) >= 5:
                unlocked = True
            
            if unlocked:
                achievement.unlocked = True
                achievement.unlock_date = datetime.datetime.now().strftime('%Y-%m-%d')
                self.user_stats['unlocked_achievements'].append(achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def get_progress_summary(self) -> Dict:
        """Get user progress summary"""
        unlocked_count = len(self.user_stats['unlocked_achievements'])
        total_count = len(self.achievements)
        
        return {
            "level": self._calculate_level(),
            "total_reps": self.user_stats['total_reps'],
            "total_sessions": self.user_stats['total_sessions'],
            "current_streak": self.user_stats['current_streak'],
            "longest_streak": self.user_stats['longest_streak'],
            "best_form_score": self.user_stats['best_form_score'],
            "achievements_unlocked": f"{unlocked_count}/{total_count}",
            "exercises_mastered": len(self.user_stats['exercises_tried'])
        }
    
    def _calculate_level(self) -> int:
        """Calculate user level based on total reps"""
        total_reps = self.user_stats['total_reps']
        if total_reps < 50:
            return 1
        elif total_reps < 200:
            return 2
        elif total_reps < 500:
            return 3
        elif total_reps < 1000:
            return 4
        else:
            return 5 + (total_reps - 1000) // 500