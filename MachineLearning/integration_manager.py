#!/usr/bin/env python3
"""
Integration Manager
Connects different components and manages data flow
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class UserSession:
    user_id: str
    session_id: str
    start_time: datetime
    exercise_type: str
    total_reps: int = 0
    avg_form_score: float = 0.0
    calories_burned: float = 0.0
    duration_minutes: float = 0.0
    achievements_unlocked: List[str] = None
    
    def __post_init__(self):
        if self.achievements_unlocked is None:
            self.achievements_unlocked = []

class IntegrationManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.setup_logging()
        
        # Component availability
        self.components = {
            "exercise_tracker": False,
            "dashboard": False,
            "audio_coach": False,
            "gamification": False,
            "analytics": False,
            "optimizer": False,
            "custom_creator": False
        }
        
        self.current_session: Optional[UserSession] = None
        self.session_data = []
        
        # Check component availability
        self.check_components()
    
    def setup_logging(self):
        """Setup logging for integration tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IntegrationManager')
    
    def check_components(self):
        """Check which components are available"""
        component_files = {
            "exercise_tracker": "advanced_bicep_tracker.py",
            "dashboard": "dashboard.py", 
            "audio_coach": "audio_coach.py",
            "gamification": "gamification.py",
            "analytics": "utils/analytics.py",
            "optimizer": "utils/optimizer.py",
            "custom_creator": "utils/custom_exercise_creator.py"
        }
        
        for component, filename in component_files.items():
            filepath = os.path.join(self.base_path, filename)
            self.components[component] = os.path.exists(filepath)
        
        self.logger.info(f"Component status: {self.components}")
    
    def start_workout_session(self, user_id: str, exercise_type: str) -> str:
        """Start a new workout session"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = UserSession(
            user_id=user_id,
            session_id=session_id,
            start_time=datetime.now(),
            exercise_type=exercise_type
        )
        
        self.logger.info(f"Started session {session_id} for user {user_id}")
        
        # Initialize components if available
        self._initialize_session_components()
        
        return session_id
    
    def _initialize_session_components(self):
        """Initialize components for the current session"""
        if not self.current_session:
            return
        
        init_data = {
            "user_id": self.current_session.user_id,
            "session_id": self.current_session.session_id,
            "exercise_type": self.current_session.exercise_type
        }
        
        # Initialize gamification
        if self.components["gamification"]:
            try:
                self._send_to_gamification("init_session", init_data)
            except Exception as e:
                self.logger.warning(f"Failed to initialize gamification: {e}")
        
        # Initialize dashboard
        if self.components["dashboard"]:
            try:
                self._send_to_dashboard("start_session", init_data)
            except Exception as e:
                self.logger.warning(f"Failed to initialize dashboard: {e}")
        
        # Initialize audio coach
        if self.components["audio_coach"]:
            try:
                self._send_to_audio_coach("session_start", init_data)
            except Exception as e:
                self.logger.warning(f"Failed to initialize audio coach: {e}")
    
    def update_session_data(self, rep_data: Dict[str, Any]):
        """Update current session with new rep data"""
        if not self.current_session:
            self.logger.warning("No active session for data update")
            return
        
        # Update session totals
        self.current_session.total_reps += 1
        
        if 'form_score' in rep_data:
            # Update average form score
            current_avg = self.current_session.avg_form_score
            total_reps = self.current_session.total_reps
            new_avg = (current_avg * (total_reps - 1) + rep_data['form_score']) / total_reps
            self.current_session.avg_form_score = new_avg
        
        # Store rep data
        rep_data['timestamp'] = datetime.now().isoformat()
        rep_data['session_id'] = self.current_session.session_id
        self.session_data.append(rep_data)
        
        # Send updates to components
        self._broadcast_rep_update(rep_data)
        
        self.logger.debug(f"Session updated: {self.current_session.total_reps} reps")
    
    def _broadcast_rep_update(self, rep_data: Dict[str, Any]):
        """Broadcast rep update to all components"""
        # Update dashboard
        if self.components["dashboard"]:
            try:
                self._send_to_dashboard("rep_completed", rep_data)
            except Exception as e:
                self.logger.warning(f"Dashboard update failed: {e}")
        
        # Update gamification
        if self.components["gamification"]:
            try:
                achievement = self._send_to_gamification("rep_completed", rep_data)
                if achievement:
                    self.current_session.achievements_unlocked.append(achievement)
                    self._send_to_audio_coach("achievement_unlocked", {"achievement": achievement})
            except Exception as e:
                self.logger.warning(f"Gamification update failed: {e}")
        
        # Update audio coach
        if self.components["audio_coach"]:
            try:
                self._send_to_audio_coach("rep_feedback", rep_data)
            except Exception as e:
                self.logger.warning(f"Audio coach update failed: {e}")
    
    def end_workout_session(self) -> Dict[str, Any]:
        """End the current workout session"""
        if not self.current_session:
            self.logger.warning("No active session to end")
            return {}
        
        # Calculate session duration
        end_time = datetime.now()
        duration = (end_time - self.current_session.start_time).total_seconds() / 60
        self.current_session.duration_minutes = duration
        
        # Estimate calories burned (simple calculation)
        self.current_session.calories_burned = self._estimate_calories()
        
        # Finalize session data
        session_summary = {
            "session_id": self.current_session.session_id,
            "user_id": self.current_session.user_id,
            "exercise_type": self.current_session.exercise_type,
            "total_reps": self.current_session.total_reps,
            "avg_form_score": self.current_session.avg_form_score,
            "duration_minutes": self.current_session.duration_minutes,
            "calories_burned": self.current_session.calories_burned,
            "achievements_unlocked": self.current_session.achievements_unlocked,
            "end_time": end_time.isoformat()
        }
        
        # Save session data
        self._save_session_data(session_summary)
        
        # Notify components
        self._broadcast_session_end(session_summary)
        
        self.logger.info(f"Session {self.current_session.session_id} completed")
        
        # Reset current session
        self.current_session = None
        self.session_data = []
        
        return session_summary
    
    def _estimate_calories(self) -> float:
        """Simple calorie estimation based on exercise type and duration"""
        if not self.current_session:
            return 0.0
        
        # Calories per minute by exercise type (rough estimates)
        calorie_rates = {
            "bicep_curls": 3.0,
            "pushups": 8.0,
            "squats": 7.0,
            "lunges": 6.0,
            "shoulder_press": 4.0,
            "default": 5.0
        }
        
        rate = calorie_rates.get(self.current_session.exercise_type, calorie_rates["default"])
        return rate * self.current_session.duration_minutes
    
    def _save_session_data(self, session_summary: Dict[str, Any]):
        """Save session data to file"""
        # Save to user's progress file
        user_file = f"user_progress_{session_summary['user_id']}.json"
        
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                user_data = json.load(f)
        else:
            user_data = {"session_history": []}
        
        user_data["session_history"].append(session_summary)
        
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        # Save detailed session data
        session_file = f"session_{session_summary['session_id']}.json"
        detailed_data = {
            "summary": session_summary,
            "rep_data": self.session_data
        }
        
        with open(session_file, 'w') as f:
            json.dump(detailed_data, f, indent=2)
    
    def _broadcast_session_end(self, session_summary: Dict[str, Any]):
        """Notify all components about session end"""
        # Update analytics
        if self.components["analytics"]:
            try:
                self._send_to_analytics("session_completed", session_summary)
            except Exception as e:
                self.logger.warning(f"Analytics update failed: {e}")
        
        # Update gamification for session achievements
        if self.components["gamification"]:
            try:
                session_achievements = self._send_to_gamification("session_completed", session_summary)
                if session_achievements:
                    self.logger.info(f"Session achievements: {session_achievements}")
            except Exception as e:
                self.logger.warning(f"Gamification session end failed: {e}")
        
        # Audio coach session summary
        if self.components["audio_coach"]:
            try:
                self._send_to_audio_coach("session_summary", session_summary)
            except Exception as e:
                self.logger.warning(f"Audio coach session end failed: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        user_file = f"user_progress_{user_id}.json"
        
        if not os.path.exists(user_file):
            return {"error": "No data found for user"}
        
        with open(user_file, 'r') as f:
            user_data = json.load(f)
        
        sessions = user_data.get("session_history", [])
        
        if not sessions:
            return {"error": "No session history"}
        
        # Calculate aggregate stats
        total_reps = sum(s.get("total_reps", 0) for s in sessions)
        total_sessions = len(sessions)
        avg_form_score = sum(s.get("avg_form_score", 0) for s in sessions) / total_sessions
        total_calories = sum(s.get("calories_burned", 0) for s in sessions)
        total_time = sum(s.get("duration_minutes", 0) for s in sessions)
        
        # Exercise variety
        exercise_types = set(s.get("exercise_type") for s in sessions)
        
        stats = {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "total_reps": total_reps,
            "avg_form_score": round(avg_form_score, 1),
            "total_calories": round(total_calories, 1),
            "total_time_minutes": round(total_time, 1),
            "exercise_variety": len(exercise_types),
            "exercises_tried": list(exercise_types),
            "last_session": sessions[-1]["end_time"] if sessions else None
        }
        
        return stats
    
    def _send_to_dashboard(self, action: str, data: Dict[str, Any]) -> Any:
        """Send data to dashboard component"""
        # This would integrate with actual dashboard module
        self.logger.debug(f"Dashboard: {action} - {data}")
        return True
    
    def _send_to_gamification(self, action: str, data: Dict[str, Any]) -> Any:
        """Send data to gamification component"""
        # This would integrate with actual gamification module
        self.logger.debug(f"Gamification: {action} - {data}")
        return None
    
    def _send_to_audio_coach(self, action: str, data: Dict[str, Any]) -> Any:
        """Send data to audio coach component"""
        # This would integrate with actual audio coach module
        self.logger.debug(f"Audio Coach: {action} - {data}")
        return True
    
    def _send_to_analytics(self, action: str, data: Dict[str, Any]) -> Any:
        """Send data to analytics component"""
        # This would integrate with actual analytics module
        self.logger.debug(f"Analytics: {action} - {data}")
        return True
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "components_available": self.components,
            "active_session": self.current_session.session_id if self.current_session else None,
            "total_components": len(self.components),
            "active_components": sum(self.components.values()),
            "system_health": "healthy" if sum(self.components.values()) >= 3 else "limited"
        }
    
    def force_component_check(self):
        """Force recheck of component availability"""
        self.check_components()
        self.logger.info("Component availability rechecked")
        return self.components

# Example usage
if __name__ == "__main__":
    manager = IntegrationManager()
    
    print("🔗 INTEGRATION MANAGER")
    print("="*30)
    
    # Show system status
    status = manager.get_system_status()
    print(f"System Health: {status['system_health']}")
    print(f"Active Components: {status['active_components']}/{status['total_components']}")
    
    print("\nComponent Status:")
    for component, available in manager.components.items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {component}")
    
    # Example session
    print("\n🏋️ Example Session:")
    session_id = manager.start_workout_session("user123", "bicep_curls")
    print(f"Started session: {session_id}")
    
    # Simulate some reps
    for i in range(3):
        rep_data = {
            "rep_number": i + 1,
            "form_score": 85 + (i * 5),
            "angle_data": {"left_elbow": 45 + (i * 10)}
        }
        manager.update_session_data(rep_data)
    
    # End session
    summary = manager.end_workout_session()
    print(f"Session completed: {summary['total_reps']} reps, {summary['avg_form_score']:.1f}% form")