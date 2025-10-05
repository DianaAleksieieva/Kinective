"use client";
import { useEffect, useState } from "react";

export default function ArmsPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState('Ready to start');
  const [currentReps, setCurrentReps] = useState(0);
  const [targetReps] = useState(10); // Target reps for completion
  const [isCompleted, setIsCompleted] = useState(false);
  const [sessionStats, setSessionStats] = useState(null);
  const [showStats, setShowStats] = useState(false);

  useEffect(() => {
    // Check if tracker is already running when component loads
    checkStatus();
    
    // Check status every 2 seconds
    const interval = setInterval(checkStatus, 2000);
    
    return () => {
      clearInterval(interval);
      // Stop tracker when leaving page
      if (isRunning) {
        stopTracker();
      }
    };
  }, []);

  const checkStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/status/biceps');
      const data = await response.json();
      setIsRunning(data.running);
      
      // Update current reps if available
      if (data.stats && data.stats.reps !== undefined) {
        setCurrentReps(data.stats.reps);
        
        // Check if target reps reached
        if (data.stats.reps >= targetReps && !isCompleted) {
          completeWorkout();
        }
      }
      
      if (data.running) {
        setStatus(`AI Bicep Tracker is running! Reps: ${currentReps}/${targetReps}`);
      } else {
        setStatus('Ready to start AI bicep curl tracking');
      }
    } catch (error) {
      setStatus('Unable to connect to AI server');
    }
  };

  const startTracker = async () => {
    try {
      setStatus('Starting AI tracker...');
      const response = await fetch('http://localhost:8000/start-exercise/biceps', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.error) {
        setStatus(`Error: ${data.error}`);
      } else {
        setStatus(data.message);
        setIsRunning(true);
      }
    } catch (error) {
      setStatus('Failed to start tracker - make sure the AI server is running');
    }
  };

  const stopTracker = async () => {
    try {
      setStatus('Stopping AI tracker...');
      const response = await fetch('http://localhost:8000/stop-exercise/biceps', {
        method: 'POST'
      });
      const data = await response.json();
      
      setStatus(data.message);
      setIsRunning(false);
    } catch (error) {
      setStatus('Failed to stop tracker');
    }
  };

  const completeWorkout = async () => {
    try {
      setStatus('🎉 Workout Complete! Getting your stats...');
      setIsCompleted(true);
      
      const response = await fetch('http://localhost:8000/complete-exercise/biceps', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.session_stats) {
        setSessionStats(data.session_stats);
        setShowStats(true);
        setStatus(data.message || '🎉 Congratulations! Workout completed!');
      }
      
      setIsRunning(false);
    } catch (error) {
      setStatus('Workout completed! (Stats unavailable)');
      setIsCompleted(true);
    }
  };

  const resetWorkout = () => {
    setIsCompleted(false);
    setCurrentReps(0);
    setSessionStats(null);
    setShowStats(false);
    setStatus('Ready to start AI bicep curl tracking');
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-8 text-center">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-purple-800 mb-4">
          💪 AI Bicep Trainer
        </h1>
        <p className="text-gray-600 max-w-md">
          Launch the professional AI bicep curl tracker with real-time pose detection and form analysis.
        </p>
      </div>

      {/* Status Display */}
      <div className="mb-8 p-6 bg-gray-100 rounded-xl max-w-lg">
        <div className="flex items-center justify-center mb-4">
          <div className={`w-3 h-3 rounded-full mr-3 ${
            isRunning ? 'bg-green-500' : 'bg-gray-400'
          }`}></div>
          <span className={`font-semibold ${
            isRunning ? 'text-green-700' : 'text-gray-700'
          }`}>
            {isRunning ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>
        <p className="text-sm text-gray-700">{status}</p>
        
        {/* Progress Bar */}
        {(isRunning || currentReps > 0) && !isCompleted && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{currentReps}/{targetReps} reps</span>
            </div>
            <div className="w-full bg-gray-300 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((currentReps / targetReps) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Completion Message & Stats */}
      {isCompleted && sessionStats && (
        <div className="mb-8 p-6 bg-gradient-to-r from-green-100 to-green-200 rounded-xl max-w-lg border-2 border-green-300">
          <div className="text-center">
            <div className="text-4xl mb-2">🎉</div>
            <h2 className="text-2xl font-bold text-green-800 mb-4">Workout Complete!</h2>
            
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-purple-700">{sessionStats.total_reps}</div>
                  <div className="text-sm text-gray-600">Total Reps</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-700">
                    {sessionStats.session_summary?.avg_form_score ? 
                      Math.round(sessionStats.session_summary.avg_form_score) : 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600">Avg Form Score</div>
                </div>
              </div>
              
              {sessionStats.session_summary?.total_time && (
                <div className="mt-3 text-center">
                  <div className="text-lg font-semibold text-gray-700">
                    Duration: {Math.round(sessionStats.session_summary.total_time / 60)} min
                  </div>
                </div>
              )}
              
              {sessionStats.exported_file && (
                <div className="mt-3 text-xs text-gray-500">
                  Session saved: {sessionStats.exported_file}
                </div>
              )}
            </div>
            
            <button
              onClick={resetWorkout}
              className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all"
            >
              Start New Workout
            </button>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      {!isCompleted && (
        <div className="flex gap-4 mb-8">
          <button
            onClick={startTracker}
            disabled={isRunning}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              isRunning
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-purple-700 hover:bg-purple-800 hover:scale-105'
            }`}
          >
            {isRunning ? 'Already Running' : 'Start AI Tracker'}
          </button>
          
          <button
            onClick={stopTracker}
            disabled={!isRunning}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              !isRunning
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700 hover:scale-105'
            }`}
          >
            Stop Tracker
          </button>
          
          <button
            onClick={completeWorkout}
            disabled={!isRunning}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              !isRunning
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 hover:scale-105'
            }`}
          >
            Complete Workout
          </button>
        </div>
      )}

      {/* Instructions */}
      {!isCompleted && (
        <div className="max-w-2xl bg-purple-50 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-purple-800 mb-3">
            📐 How to Use:
          </h3>
          <div className="text-left text-gray-700 space-y-2">
            <div>• Click "Start AI Tracker" to begin your workout</div>
            <div>• Position yourself sideways to the camera (side view)</div>
            <div>• Make sure your arm holding the weight is visible</div>
            <div>• Do {targetReps} bicep curls for a complete workout</div>
            <div>• The AI will automatically complete when you reach {targetReps} reps</div>
            <div>• Or click "Complete Workout" to finish early and see your stats</div>
          </div>
        </div>
      )}
    </div>
  );
}
