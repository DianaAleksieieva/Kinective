"use client";
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function ProfilePage() {
  // Simulated user data — later this can be fetched from backend
  const [streak, setStreak] = useState(7);
  const [workoutsThisMonth, setWorkoutsThisMonth] = useState(12);
  const [monthlyData, setMonthlyData] = useState([]);

  useEffect(() => {
    // Mock monthly data (could be replaced with real backend data)
    const days = Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      workouts: Math.random() > 0.7 ? 1 : 0, // randomly simulating
    }));
    setMonthlyData(days);
  }, []);

  return (
    <div className="flex flex-col items-center justify-start w-full max-w-2xl mx-auto p-6 text-center">
      {/* Header */}
      <h1 className="text-4xl font-extrabold text-neonGreen drop-shadow-[0_0_8px_#39FF14] mb-4">
        👤 Your Profile
      </h1>

      {/* User Info Card */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-md w-full mb-6">
        <h2 className="text-2xl text-neonGreen font-bold mb-2">Hasan Uddin</h2>
        <p className="text-neonGreen/80">Fitness Enthusiast 🏋</p>
        <p className="text-neonGreen/70 text-sm">Joined: Jan 2025</p>
      </div>

      {/* Streak Section */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-md w-full mb-6 flex flex-col items-center">
        <h3 className="text-xl font-bold text-neonGreen mb-2">🔥 Workout Streak</h3>
        <p className="text-3xl font-extrabold text-neonGreen">{streak} days</p>
        <p className="text-neonGreen/70 text-sm">Keep it going! 💪</p>
      </div>

      {/* Monthly Activity Graph */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-md w-full mb-6">
        <h3 className="text-xl font-bold text-neonGreen mb-4">📊 Monthly Workout Activity</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#5A3D9C" />
              <XAxis dataKey="day" stroke="#39FF14" />
              <YAxis stroke="#39FF14" />
              <Tooltip />
              <Bar dataKey="workouts" fill="#39FF14" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats / Achievements */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-md w-full mb-6 grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-lg font-bold text-neonGreen">💪 Total Workouts</h4>
          <p className="text-2xl font-extrabold text-neonGreen">{workoutsThisMonth}</p>
          <p className="text-neonGreen/70 text-sm">This month</p>
        </div>
        <div>
          <h4 className="text-lg font-bold text-neonGreen">🏅 Personal Best</h4>
          <p className="text-2xl font-extrabold text-neonGreen">15 days</p>
          <p className="text-neonGreen/70 text-sm">Longest streak</p>
        </div>
      </div>
    </div>
  );
}
