from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime

app = FastAPI(title="Kinective AI Fitness API", version="1.0.0")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track running exercise processes
running_processes = {}
exercise_trackers = {}  # Store tracker instances for stats

@app.get("/")
def root():
    return {"message": "Kinective AI Fitness API is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "available_exercises": ["squats", "biceps", "pushups", "lunges", "shoulders"]
    }

@app.post("/start-exercise/{exercise_type}")
async def start_exercise(exercise_type: str):
    """Start the AI exercise tracker directly with OpenCV display"""
    
    # Stop any existing process for this exercise
    if exercise_type in running_processes:
        await stop_exercise(exercise_type)
    
    try:
        # Get the parent directory (where the Python trackers are located)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Map exercise types to their Python files
        exercise_files = {
            "squats": "advanced_squat_tracker.py",
            "biceps": "advanced_bicep_tracker.py", 
            "pushups": "advanced_pushup_tracker.py",
            "lunges": "advanced_lunge_tracker.py",
            "shoulders": "advanced_shoulder_tracker.py"
        }
        
        if exercise_type not in exercise_files:
            return {"error": f"Unknown exercise type: {exercise_type}"}
        
        script_path = os.path.join(parent_dir, exercise_files[exercise_type])
        
        if not os.path.exists(script_path):
            return {"error": f"Exercise script not found: {script_path}"}
        
        # Start the Python tracker process with GUI support
        process = subprocess.Popen([
            sys.executable, script_path
        ], cwd=parent_dir, 
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        
        running_processes[exercise_type] = process
        
        # Wait a moment to see if there are immediate errors
        import time
        time.sleep(2)  # Give more time for GUI to start
        
        if process.poll() is not None:
            # Process ended immediately - there was an error
            return {
                "error": f"Exercise script failed to start - process ended immediately",
                "script_path": script_path
            }
        
        return {
            "status": "started",
            "exercise": exercise_type,
            "message": f"AI {exercise_type} tracker started! Look for the OpenCV window.",
            "process_id": process.pid,
            "script_path": script_path
        }
        
    except Exception as e:
        return {"error": f"Failed to start exercise: {str(e)}"}

@app.post("/stop-exercise/{exercise_type}")
async def stop_exercise(exercise_type: str):
    """Stop the running exercise tracker"""
    
    if exercise_type not in running_processes:
        return {"message": f"No {exercise_type} tracker is currently running"}
    
    try:
        process = running_processes[exercise_type]
        
        # Terminate the process
        process.terminate()
        
        # Wait a bit for graceful shutdown
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't stop gracefully
            process.kill()
            process.wait()
        
        del running_processes[exercise_type]
        
        return {
            "status": "stopped",
            "exercise": exercise_type,
            "message": f"AI {exercise_type} tracker stopped"
        }
        
    except Exception as e:
        return {"error": f"Failed to stop exercise: {str(e)}"}

@app.get("/status/{exercise_type}")
def get_exercise_status(exercise_type: str):
    """Check if an exercise tracker is currently running"""
    
    if exercise_type not in running_processes:
        return {"running": False, "exercise": exercise_type, "stats": {"reps": 0}}
    
    process = running_processes[exercise_type]
    
    # Check if process is still alive
    if process.poll() is None:
        # Try to read progress from file
        stats = {"reps": 0}
        try:
            # Look for progress file in parent directory (where Python scripts run)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            progress_file = os.path.join(parent_dir, f"{exercise_type}_progress.json")
            
            print(f"Looking for progress file at: {progress_file}")
            print(f"File exists: {os.path.exists(progress_file)}")
            
            if os.path.exists(progress_file):
                import json
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                    stats = {
                        "reps": progress_data.get("rep_count", 0),
                        "stage": progress_data.get("stage", "unknown"),
                        "form_score": progress_data.get("form_score", 0)
                    }
                    print(f"Read progress data: {stats}")
        except Exception as e:
            print(f"Error reading progress file: {e}")
            # If file reading fails, just return basic stats
            stats = {"reps": 0}
        
        return {
            "running": True,
            "exercise": exercise_type,
            "process_id": process.pid,
            "stats": stats
        }
    else:
        # Process has ended, remove it from tracking
        del running_processes[exercise_type]
        return {"running": False, "exercise": exercise_type, "stats": {"reps": 0}}

@app.post("/stop-all")
async def stop_all_exercises():
    """Stop all running exercise trackers"""
    
    stopped_exercises = []
    
    for exercise_type in list(running_processes.keys()):
        result = await stop_exercise(exercise_type)
        stopped_exercises.append({
            "exercise": exercise_type,
            "result": result
        })
    
    return {
        "message": "All exercise trackers stopped",
        "stopped_exercises": stopped_exercises
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

def process_exercise_frame(frame, exercise_type):
    """Process a frame with the appropriate exercise tracker"""
    tracker = exercise_trackers[exercise_type]
    
    if tracker is None:
        return {
            "frame": frame,
            "stats": {"error": "Tracker not initialized"},
            "feedback": "AI tracker not available"
        }
    
    try:
        # Run pose estimation
        results = tracker.model(frame, conf=0.5, verbose=False)
        
        if results and len(results) > 0 and results[0].keypoints is not None and len(results[0].keypoints.data) > 0:
            keypoints = results[0].keypoints.data[0].cpu().numpy()
            
            # Process based on exercise type
            if exercise_type == "squats":
                # Use squat analysis method
                result = tracker.analyze_squat_advanced(keypoints)
                if result and len(result) == 2:
                    knee_angle, feedback = result
                    # Draw pose information on frame
                    tracker.draw_squat_pose_info(frame, keypoints, knee_angle)
                    tracker.draw_squat_ui(frame, knee_angle)
                    
                    stats = {
                        "reps": tracker.rep_count,
                        "knee_angle": knee_angle,
                        "stage": tracker.stage,
                        "form": "Good" if knee_angle and knee_angle <= 100 else "Fair"
                    }
                    feedback_text = " | ".join(feedback[-2:]) if feedback else "Keep going!"
                else:
                    stats = {"reps": tracker.rep_count, "error": "Analysis failed"}
                    feedback_text = "Position yourself in view"
                    
            elif exercise_type == "biceps":
                # Use bicep analysis method  
                result = tracker.analyze_bicep_curl_advanced(keypoints)
                if result and len(result) == 2:
                    arm_angle, feedback = result
                    # Draw pose information on frame
                    tracker.draw_advanced_pose_info(frame, keypoints, arm_angle)
                    tracker.draw_advanced_ui(frame, arm_angle)
                    
                    stats = {
                        "reps": tracker.rep_count,
                        "arm_angle": arm_angle,
                        "stage": tracker.stage,
                        "form": "Good" if arm_angle else "Unknown"
                    }
                    feedback_text = " | ".join(feedback[-2:]) if feedback else "Keep going!"
                else:
                    stats = {"reps": tracker.rep_count, "error": "Analysis failed"}
                    feedback_text = "Position your arm in view"
                    
            elif exercise_type == "pushups":
                # Use pushup analysis method
                # Note: This would need to be adapted based on the pushup tracker's interface
                stats = {"reps": tracker.rep_count, "form": "Unknown"}
                feedback_text = "Pushup tracking active"
            else:
                return {
                    "frame": frame,
                    "stats": {"error": "Unknown exercise type"},
                    "feedback": "Unknown exercise"
                }
        else:
            stats = {"reps": exercise_trackers[exercise_type].rep_count if exercise_trackers[exercise_type] else 0}
            feedback_text = "No person detected - step into view"
        
        return {
            "frame": frame,
            "stats": stats,
            "feedback": feedback_text
        }
        
    except Exception as e:
        print(f"Error in process_exercise_frame: {e}")
        return {
            "frame": frame,
            "stats": {"error": str(e)},
            "feedback": "Processing error"
        }

@app.post("/complete-exercise/{exercise_type}")
async def complete_exercise(exercise_type: str):
    """Complete exercise session and return stats"""
    try:
        # Stop the exercise first
        stop_result = await stop_exercise(exercise_type)
        
        # Get the tracker instance if available
        if exercise_type in exercise_trackers and exercise_trackers[exercise_type]:
            tracker = exercise_trackers[exercise_type]
            
            # Get session stats
            session_stats = {
                "exercise_type": exercise_type,
                "total_reps": tracker.rep_count,
                "active_arm": getattr(tracker, 'active_arm', 'right'),
                "completion_time": datetime.now().isoformat(),
                "session_summary": {}
            }
            
            # Get detailed stats if rep data exists
            if hasattr(tracker, 'rep_data') and tracker.rep_data:
                import numpy as np
                rep_data = tracker.rep_data
                session_stats["session_summary"] = {
                    "avg_form_score": float(np.mean([rep.get('rom_score', 0) for rep in rep_data])),
                    "avg_smoothness": float(np.mean([rep.get('smoothness', 0) for rep in rep_data])),
                    "total_time": len(rep_data) * 30,  # Approximate
                    "rep_breakdown": rep_data[-5:] if len(rep_data) > 5 else rep_data  # Last 5 reps
                }
            
            # Export session data if the method exists
            if hasattr(tracker, 'export_session_data'):
                try:
                    filename = tracker.export_session_data()
                    session_stats["exported_file"] = filename
                except Exception as e:
                    session_stats["export_error"] = str(e)
            
            return {
                "status": "completed",
                "message": f"Great job! You completed {tracker.rep_count} {exercise_type} reps!",
                "session_stats": session_stats,
                "stop_result": stop_result
            }
        else:
            return {
                "status": "completed",
                "message": f"Exercise {exercise_type} completed",
                "session_stats": {"total_reps": 0, "exercise_type": exercise_type},
                "stop_result": stop_result
            }
            
    except Exception as e:
        return {
            "error": f"Failed to complete exercise: {str(e)}",
            "status": "error"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
