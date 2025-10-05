"use client";
import { useEffect, useState } from "react";

export default function SquatsPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState('Ready to start');

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
      const response = await fetch('http://localhost:8001/status/squats');
      const data = await response.json();
      setIsRunning(data.running);
      
      if (data.running) {
        setStatus('AI Squat Tracker is running! Check the OpenCV window.');
      } else {
        setStatus('Ready to start AI squat tracking');
      }
    } catch (error) {
      setStatus('Unable to connect to AI server');
    }
  };

  const startTracker = async () => {
    try {
      setStatus('Starting AI tracker...');
      const response = await fetch('http://localhost:8001/start-exercise/squats', {
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
      const response = await fetch('http://localhost:8001/stop-exercise/squats', {
        method: 'POST'
      });
      const data = await response.json();
      
      setStatus(data.message);
      setIsRunning(false);
    } catch (error) {
      setStatus('Failed to stop tracker');
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-8 text-center">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-purple-800 mb-4">
          🦵 AI Squat Trainer
        </h1>
        <p className="text-gray-600 max-w-md">
          Launch the professional AI squat tracker with real-time pose detection and form analysis.
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
      </div>

      {/* Control Buttons */}
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
      </div>

      {/* Instructions */}
      <div className="max-w-2xl bg-purple-50 p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-purple-800 mb-3">
          📐 How to Use:
        </h3>
        <div className="text-left text-gray-700 space-y-2">
          <div>• Click "Start AI Tracker" to launch the professional OpenCV window</div>
          <div>• Position yourself 4-5 feet from your webcam</div>
          <div>• Make sure your full body is visible in the frame</div>
          <div>• Start doing squats - the AI will track your form and count reps</div>
          <div>• Press 'q' in the OpenCV window to quit</div>
          <div>• Use 'r' to reset your rep count during the session</div>
        </div>
        
        <div className="mt-4 p-3 bg-yellow-100 border-l-4 border-yellow-500 rounded">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> The AI tracker runs in a separate OpenCV window with the same smooth performance as your original Python scripts.
          </p>
        </div>
      </div>
    </div>
  );
}
