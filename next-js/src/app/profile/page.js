"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase"; // make sure this is your firebase config
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";

export default function ProfilePage() {
  const [showVideo, setShowVideo] = useState(false);
  const [library, setLibrary] = useState([]);
  const [lastVideo, setLastVideo] = useState(null);

  useEffect(() => {
    async function fetchLibrary() {
      try {
        // 🔹 Replace "default" with the real userId if you have authentication
        const userRef = doc(db, "users", "default");
        const snap = await getDoc(userRef);

        if (snap.exists()) {
          const data = snap.data();
          if (data.library && Array.isArray(data.library)) {
            setLibrary(data.library);
            setLastVideo(data.library[data.library.length - 1] || null);
          }
        }
      } catch (err) {
        console.error("❌ Error fetching library:", err);
      }
    }
    fetchLibrary();
  }, []);

  const handleOpenVideo = () => setShowVideo(true);
  const handleCloseVideo = () => setShowVideo(false);

  // Example chart data
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
        <div className="flex-1 text-center sm:text-left">
          <h2 className="text-2xl font-bold text-black">Hasan Uddin</h2>
          <p className="text-black/80 text-sm">Fitness Enthusiast 🏋</p>
          <p className="text-black/60 text-xs">Joined: Jan 2025</p>
        </div>

        {/* 📚 Library Button */}
        <Link
          href="/library"
          className="flex items-center justify-center w-16 h-16 bg-purple-900 rounded-xl shadow-lg hover:scale-110 transition relative group"
          aria-label="Go to Video Library"
        >
          <div className="w-10 h-10 bg-green-400 rounded-full flex items-center justify-center group-hover:scale-110 transition">
            📚
          </div>
        </Link>

        {/* ▶ Play Button */}
        {lastVideo && (
          <button
            onClick={handleOpenVideo}
            className="flex items-center justify-center w-16 h-16 bg-purple-900 rounded-xl shadow-lg hover:scale-110 transition relative group"
            aria-label="Play Profile Video"
          >
            <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center group-hover:scale-110 transition">
              ▶
            </div>
          </button>
        )}
      </div>

      {/* 🔥 Streak */}
      <div className="bg-purple-800/40 p-5 rounded-xl shadow-lg w-full mb-6 text-center">
        <h3 className="text-xl font-semibold text-black mb-2">🔥 Workout Streak</h3>
        <p className="text-3xl font-extrabold text-black">{streak} days</p>
        <p className="text-black/70 text-sm">Keep it going! 💪</p>
      </div>

      {/* 📊 Chart */}
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

      {/* 🏆 Stats */}
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
      {showVideo && lastVideo && (
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
              src={lastVideo.replace("watch?v=", "embed/")} // 🔹 auto convert YouTube
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
