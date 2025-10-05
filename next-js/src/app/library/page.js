"use client";
import { useState, useEffect } from "react";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function LibraryPage() {
  const [videos, setVideos] = useState([]);
  const [lastWeeklyPlan, setLastWeeklyPlan] = useState(null);
  const [watched, setWatched] = useState({});

  useEffect(() => {
    async function fetchLibraryData() {
      try {
        const userRef = doc(db, "users", "default");
        const snap = await getDoc(userRef);

        if (!snap.exists()) return;
        const data = snap.data();

        // 🎥 Load videos
        let parsedVideos = [];
        if (typeof data.library === "string") {
          try {
            parsedVideos = JSON.parse(data.library);
          } catch (err) {
            console.error("❌ Failed to parse library string:", err);
          }
        } else if (Array.isArray(data.library)) {
          parsedVideos = data.library;
        }
        parsedVideos = parsedVideos.filter((v) => v && v.trim() !== "");
        setVideos(parsedVideos);

        // 📅 Load last weekly plan
        if (data.weeklyPlans && Array.isArray(data.weeklyPlans)) {
          const lastPlan = data.weeklyPlans[data.weeklyPlans.length - 1];
          setLastWeeklyPlan(lastPlan);
        }
      } catch (err) {
        console.error("❌ Error fetching library:", err);
      }
    }

    fetchLibraryData();
  }, []);
  // 🔹 Remove a video from the current weekly plan (and update Firestore)
  const removeWeeklyVideo = async (indexToRemove) => {
    try {
      if (!lastWeeklyPlan) return;

      // 1️⃣ Filter out the removed day locally
      const updatedDays = lastWeeklyPlan.days.filter(
        (_, idx) => idx !== indexToRemove
      );
      const updatedPlan = { ...lastWeeklyPlan, days: updatedDays };

      // 2️⃣ Update Firestore
      const userRef = doc(db, "users", "default");
      const snap = await getDoc(userRef);
      if (snap.exists()) {
        const data = snap.data();

        // Find and replace the last plan in the array
        if (Array.isArray(data.weeklyPlans) && data.weeklyPlans.length > 0) {
          const plans = [...data.weeklyPlans];
          plans[plans.length - 1] = updatedPlan;

          await updateDoc(userRef, { weeklyPlans: plans });
        }
      }

      // 3️⃣ Update React state to match
      setLastWeeklyPlan(updatedPlan);
    } catch (err) {
      console.error("❌ Error removing weekly video:", err);
    }
  };

  const toggleWatched = (url) => {
    setWatched((prev) => ({ ...prev, [url]: !prev[url] }));
  };

  const removeVideo = async (url) => {
    try {
      const updated = videos.filter((v) => v !== url);
      setVideos(updated);

      const userRef = doc(db, "users", "default");
      await updateDoc(userRef, { library: updated });
    } catch (err) {
      console.error("❌ Error removing video:", err);
    }
  };

  const renderVideoEmbed = (url) => {
    if (url.includes("youtube.com") || url.includes("youtu.be")) {
      return (
        <iframe
          src={url.replace("watch?v=", "embed/")}
          className="w-full aspect-video rounded-lg"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      );
    } else if (url.includes("vimeo.com")) {
      return (
        <iframe
          src={url}
          className="w-full aspect-video rounded-lg"
          allow="autoplay; fullscreen; picture-in-picture"
          allowFullScreen
        />
      );
    } else {
      return <video src={url} controls className="w-full rounded-lg" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 text-gray-900 p-8">
      <h1 className="text-4xl font-extrabold text-center mb-10">
        🎥 My Workout Library
      </h1>

      {/* 🗓 WEEKLY PLAN */}
      <section className="mb-12">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">🗓 Last Weekly Plan</h2>
        </div>

        {!lastWeeklyPlan ? (
          <p className="text-gray-600 text-center">
            No weekly plan saved yet 💡
          </p>
        ) : (
          <>
            <div className="text-center mb-6">
              <p className="text-sm text-gray-500">
                Saved on {new Date(lastWeeklyPlan.createdAt).toLocaleString()}
              </p>
            </div>

            {/* 🧩 Video Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {lastWeeklyPlan.days.map((day, i) => (
                <div
                  key={i}
                  className="bg-[#F4E6FF] rounded-2xl shadow-md hover:shadow-lg transition flex flex-col p-4"
                >
                  <div className="font-semibold text-gray-800 mb-1">
                    {day.day}:{" "}
                    <span className="text-[#6A00B9]">
                      {day.name || "Suggested workout"}
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                    {day.description ||
                      "Exercise video for your daily workout plan."}
                  </p>

                  {/* 🎥 Video */}
                  <div className="relative rounded-lg overflow-hidden bg-white">
                    {day.video && renderVideoEmbed(day.video)}
                  </div>

                  {/* ✅ Action buttons */}
                  {day.video && (
                    <div className="flex justify-between items-center mt-3 p-2 rounded-lg">
                      {/* Mark Watched */}
                      <button
                        onClick={() => toggleWatched(day.video)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 shadow-sm ${
                          watched[day.video]
                            ? "bg-[#32D198] text-white hover:bg-[#28B886]"
                            : "bg-[#E6FFF3] text-gray-900 hover:bg-[#C9F5E2] border border-[#32D198]/40"
                        }`}
                      >
                        {watched[day.video] ? "✅ Watched" : "Mark Watched"}
                      </button>

                      {/* Remove (optional: only hides locally) */}
                      <button
                        onClick={() => removeWeeklyVideo(i)}
                        className="px-3 py-1.5 rounded-lg text-sm font-semibold bg-[#E86BC6] text-white hover:bg-[#D259B1] transition-all duration-200 shadow-sm"
                      >
                        🗑 Remove
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </section>

      {/* 🎬 SAVED VIDEOS */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">📁 Saved Videos</h2>
        </div>

        {videos.length === 0 ? (
          <p className="text-center text-gray-600">
            No individual videos saved yet 📼
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((url) => (
              <div
                key={url}
                className="bg-white rounded-2xl shadow-md hover:shadow-lg transition flex flex-col p-3"
              >
                {/* 🎥 Video Embed */}
                <div className="relative rounded-lg overflow-hidden">
                  {renderVideoEmbed(url)}
                </div>

                {/* Buttons Section */}
                <div className="flex justify-between items-center mt-3 bg-[#FAFAFA] p-2 rounded-lg">
                  {/* ✅ Watched / Mark Watched */}
                  <button
                    onClick={() => toggleWatched(url)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 shadow-sm ${
                      watched[url]
                        ? "bg-[#32D198] text-white hover:bg-[#28B886]" // Neo Mint active
                        : "bg-[#E6FFF3] text-gray-900 hover:bg-[#C9F5E2] border border-[#32D198]/40"
                    }`}
                  >
                    {watched[url] ? "✅ Watched" : "Mark Watched"}
                  </button>

                  {/* 🗑 Remove */}
                  <button
                    onClick={() => removeVideo(url)}
                    className="px-3 py-1.5 rounded-lg text-sm font-semibold bg-[#E86BC6] text-white hover:bg-[#D259B1] transition-all duration-200 shadow-sm"
                  >
                    🗑 Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
