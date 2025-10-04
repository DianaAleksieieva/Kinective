"use client";
import { useState, useEffect } from "react";

// 🧠 Helper to calculate streaks based on workout dates
function calculateStreak(workouts) {
  if (!workouts || workouts.length === 0) return 0;

  // Sort dates (newest first)
  const sorted = [...workouts].sort(
    (a, b) => new Date(b.date) - new Date(a.date)
  );

  let streak = 0;
  let currentDate = new Date();
  currentDate.setHours(0, 0, 0, 0);

  for (const w of sorted) {
    const workoutDate = new Date(w.date);
    workoutDate.setHours(0, 0, 0, 0);

    const diffDays = Math.floor(
      (currentDate - workoutDate) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0 || diffDays === streak) {
      streak++;
      currentDate.setDate(currentDate.getDate() - 1);
    } else {
      break;
    }
  }

  return streak;
}

export default function HistoryPage() {
  const [type, setType] = useState("Cardio");
  const [duration, setDuration] = useState(30);
  const [message, setMessage] = useState("");
  const [workouts, setWorkouts] = useState([]);
  const [streak, setStreak] = useState(0);

  // ✅ Load saved workouts when page loads
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("kinectiveUserData")) || { workouts: [] };
    setWorkouts(saved.workouts);
    setStreak(calculateStreak(saved.workouts));
  }, []);

  // ✅ Add new workout & update streak
  const handleAddWorkout = () => {
    const today = new Date().toISOString().split("T")[0];
    const newEntry = { date: today, type, duration };

    const updated = [...workouts.filter(w => w.date !== today), newEntry];
    localStorage.setItem("kinectiveUserData", JSON.stringify({ workouts: updated }));

    setWorkouts(updated);
    setStreak(calculateStreak(updated));
    setMessage(`✅ Saved ${duration} mins of ${type}!`);
    setTimeout(() => setMessage(""), 2000);
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-6 text-center gap-6 w-full max-w-lg mx-auto">
      <h1 className="text-4xl font-extrabold text-neonGreen">📅 Workout History</h1>

      {/* 🔥 Current Streak */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-md w-full text-center">
        <h3 className="text-xl font-bold text-neonGreen mb-1">🔥 Current Streak</h3>
        <p className="text-3xl font-extrabold text-neonGreen">{streak} day{streak !== 1 ? "s" : ""}</p>
      </div>

      {/* 📝 Add Workout Form */}
      <div className="bg-purple-800/30 p-4 rounded-xl w-full text-left">
        <label className="text-neonGreen">Workout Type</label>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full rounded-lg p-2 text-purple-900 mt-1"
        >
          <option>Cardio</option>
          <option>Strength</option>
          <option>Yoga</option>
          <option>Stretch</option>
        </select>

        <label className="text-neonGreen mt-2 block">Duration (minutes)</label>
        <input
          type="number"
          min="5"
          value={duration}
          onChange={(e) => setDuration(parseInt(e.target.value))}
          className="w-full rounded-lg p-2 text-purple-900 mt-1"
        />

        <button
          onClick={handleAddWorkout}
          className="bg-neonGreen text-purple-900 px-6 py-2 mt-4 rounded-lg font-bold w-full hover:scale-105 transition"
        >
          Save Workout
        </button>

        {message && <p className="text-neonGreen mt-3 text-center">{message}</p>}
      </div>

      {/* 📊 Workout History List */}
      <div className="bg-purple-800/30 p-4 rounded-xl w-full text-left">
        <h2 className="text-xl font-bold text-neonGreen mb-3 text-center">Workout Log</h2>
        {workouts.length === 0 ? (
          <p className="text-neonGreen/70 text-center">No workouts logged yet.</p>
        ) : (
          <ul className="text-neonGreen/90 space-y-2">
            {workouts
              .sort((a, b) => new Date(b.date) - new Date(a.date))
              .map((w, idx) => (
                <li key={idx}>
                  <strong>{w.date}</strong> — {w.type} ({w.duration} min)
                </li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}
