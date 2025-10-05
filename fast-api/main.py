from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import os
import sys
from typing import Dict, Any

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
        
        # Start the Python tracker process
        process = subprocess.Popen([
            sys.executable, script_path
        ], cwd=parent_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        running_processes[exercise_type] = process
        
        # Wait a moment to see if there are immediate errors
        import time
        time.sleep(1)
        
        if process.poll() is not None:
            # Process ended immediately - there was an error
            stdout, stderr = process.communicate()
            return {
                "error": f"Exercise script failed to start",
                "stdout": stdout,
                "stderr": stderr,
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
        return {"running": False, "exercise": exercise_type}
    
    process = running_processes[exercise_type]
    
    # Check if process is still alive
    if process.poll() is None:
        return {
            "running": True,
            "exercise": exercise_type,
            "process_id": process.pid
        }
    else:
        # Process has ended, remove it from tracking
        del running_processes[exercise_type]
        return {"running": False, "exercise": exercise_type}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
