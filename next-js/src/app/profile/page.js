"use client";
import { useState } from "react";
import Link from "next/link";
import { BarChart, Bar, CartesianGrid, XAxis, YAxis, ResponsiveContainer } from "recharts";

export default function ProfilePage() {
  const [showVideo, setShowVideo] = useState(false);
  const handleOpenVideo = () => setShowVideo(true);
  const handleCloseVideo = () => setShowVideo(false);

  // Example data for chart
  const monthlyData = Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    workouts: Math.random() > 0.7 ? 1 : 0,
  }));

  const streak = 7;
  const totalWorkouts = 12;
  const personalBest = 15;

  return (
    <div className="flex flex-col items-center justify-start w-full max-w-2xl mx-auto p-4">
      {/* 🧍 Profile Header */}
      <h1 className="text-3xl font-extrabold text-black mb-6 flex items-center gap-2">
        <span className="text-green-400 text-4xl">👤</span> Your Profile
      </h1>

      {/* 📝 User Info Card */}
      <div className="relative bg-purple-800/40 p-5 rounded-xl shadow-lg w-full mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* 👤 User Info */}
        <div className="flex-1 text-center sm:text-left">
          <h2 className="text-2xl font-bold text-black">Hasan Uddin</h2>
          <p className="text-black/80 text-sm">Fitness Enthusiast 🏋</p>
          <p className="text-black/60 text-xs">Joined: Jan 2025</p>
        </div>

        {/* 📚 Styled Video Library Button with Library Icon */}
        <Link
          href="/library"
          className="order-1 sm:order-1 flex items-center justify-center w-16 h-16 bg-purple-900 rounded-xl shadow-lg hover:scale-110 transition relative group"
          aria-label="Go to Video Library"
        >
          <div className="w-10 h-10 bg-green-400 rounded-full flex items-center justify-center group-hover:scale-110 transition">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="white"
              viewBox="0 0 24 24"
              width="26"
              height="26"
            >
              <path d="M4 22h2V2H4v20zm14-20v20h2V2h-2zM9 22h6V2H9v20z" />
            </svg>
          </div>
        </Link>

        {/* ▶ Red Play Button */}
        <button
          onClick={handleOpenVideo}
          className="order-2 sm:order-2 flex items-center justify-center w-16 h-16 bg-purple-900 rounded-xl shadow-lg hover:scale-110 transition relative group"
          aria-label="Play Video"
        >
          <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center group-hover:scale-110 transition">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="white"
              viewBox="0 0 24 24"
              width="26"
              height="26"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </button>
      </div>

      {/* 🔥 Streak Section */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-lg w-full mb-6 text-center">
        <h3 className="text-xl font-semibold text-black mb-2">🔥 Workout Streak</h3>
        <p className="text-3xl font-extrabold text-black">{streak} days</p>
        <p className="text-black/70 text-sm">Keep it going! 💪</p>
      </div>

      {/* 📊 Monthly Activity Graph */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-lg w-full mb-6">
        <h3 className="text-xl font-bold text-black mb-4">📊 Monthly Workout Activity</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#999" />
              <XAxis dataKey="day" stroke="#000" />
              <YAxis stroke="#000" />
              <Bar dataKey="workouts" fill="#39FF14" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 🏆 Stats Section */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-lg w-full flex justify-around text-center">
        <div>
          <h4 className="font-bold text-black">💪 Total Workouts</h4>
          <p className="text-2xl font-extrabold text-black">{totalWorkouts}</p>
          <p className="text-black/70 text-sm">This month</p>
        </div>
        <div>
          <h4 className="font-bold text-black">🏅 Personal Best</h4>
          <p className="text-2xl font-extrabold text-black">{personalBest} days</p>
          <p className="text-black/70 text-sm">Longest streak</p>
        </div>
      </div>

      {/* 🎬 Video Popup */}
      {showVideo && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50">
          <div className="relative bg-white rounded-lg overflow-hidden shadow-2xl max-w-3xl w-full aspect-video">
            <button
              onClick={handleCloseVideo}
              className="absolute top-2 right-2 bg-black/70 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black"
            >
              ✕
            </button>

            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1"
              title="Profile Video"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      )}
    </div>
  );
}
