"use client";
import { useState } from "react";
import { doc, setDoc, arrayUnion } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function WorkOutPlanPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  // 🔹 Save Weekly Plan
  async function saveWeeklyPlanToLibrary(plan) {
    if (!plan || !Array.isArray(plan) || plan.length === 0) {
      alert("No weekly plan to save.");
      return;
    }

    try {
      const userRef = doc(db, "users", "default");
      const planData = {
        name: query || "Unnamed Plan",
        createdAt: new Date().toISOString(),
        days: plan.map((d) => ({
          day: d.day,
          name: d.name || "",
          description: d.description || "",
          video: d.video || "",
        })),
      };

      await setDoc(
        userRef,
        { weeklyPlans: arrayUnion(planData) },
        { merge: true }
      );

      alert("✅ Weekly plan saved successfully!");
    } catch (err) {
      console.error("❌ Error saving weekly plan:", err);
      alert("Failed to save weekly plan.");
    }
  }

  // 🔹 Save video to Firebase
  async function saveVideoToLibrary(videoUrl) {
    try {
      const userRef = doc(db, "users", "default");
      await setDoc(userRef, { library: arrayUnion(videoUrl) }, { merge: true });
      alert("✅ Video saved to library!");
    } catch (err) {
      console.error("❌ Error saving video:", err);
      alert("Failed to save video.");
    }
  }

  // 🔹 Extract YouTube ID
  function extractYouTubeId(url) {
    if (!url || typeof url !== "string") return null;
    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([\w-]{11})/,
      /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([\w-]{11})/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([\w-]{11})/,
    ];
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    return null;
  }

  // 🔹 Extract Vimeo ID
  function extractVimeoId(url) {
    if (!url || typeof url !== "string") return null;
    const match = url.match(/(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)/);
    return match ? match[1] : null;
  }

  // 🔹 Fetch exercises (single search)
  async function fetchExercises(userQuery) {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch("/api/exercise", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("❌ Error fetching exercises:", err);
      setError(err.message);
    }

    setLoading(false);
  }

  // 🔹 Fetch weekly plan
  async function fetchWeeklyPlan(userQuery) {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch("/api/weeklyPlan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("❌ Error fetching weekly plan:", err);
      setError(err.message);
    }

    setLoading(false);
  }

  // 🔹 Quick Filters
  const quickFilters = [
    // ⏱️ Duration filters
    { label: "< 10 min", query: "quick 10 min workout exercise video" },
    { label: "10–20 min", query: "20 min workout exercise video" },

    // 💪 Muscle groups
    { label: "Arms", query: "arm exercise video" },
    { label: "Biceps", query: "bicep exercise workout video" },
    { label: "Legs", query: "leg workout exercise video" },
    { label: "Core", query: "core strengthening exercise video" },

    // ☀️ Routines
    { label: "Morning", query: "morning stretch exercise video" },
    { label: "Evening Stretch", query: "evening stretching routine video" },
    { label: "Cardio", query: "cardio workout exercise video" },

    // 🧠 Physical Therapy & Posture
    { label: "Posture Fix", query: "posture correction exercise video" },
    {
      label: "Neck & Shoulders",
      query: "neck and shoulder mobility posture video",
    },
    { label: "Back Relief", query: "lower back pain relief exercise video" },
    {
      label: "Spine Alignment",
      query: "spine alignment physical therapy video",
    },
    {
      label: "Desk Recovery",
      query: "desk posture stretch and mobility video",
    },
    {
      label: "Balance & Stability",
      query: "balance and coordination physical therapy video",
    },
    {
      label: "Mobility Flow",
      query: "full body mobility physical therapy routine video",
    },
    {
      label: "Shoulder Rehab",
      query: "shoulder rehabilitation physical therapy exercise video",
    },
    {
      label: "Knee Stability",
      query: "knee strengthening and stability exercise video",
    },
    {
      label: "Pain Relief",
      query: "pain relief gentle stretching physical therapy video",
    },
  ];

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-center mb-4">Workout Planner</h1>

      {/* Search box */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Search or type exercise..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => fetchExercises(query)}
          className="bg-[#32D198] hover:bg-[#28B886] px-4 py-2 rounded-lg text-white transition-colors duration-200"
        >
          Search
        </button>

        <button
          onClick={() => fetchWeeklyPlan(query)}
          className="bg-[#E86BC6] hover:bg-[#D259B1] px-4 py-2 rounded-lg text-white transition-colors duration-200"
        >
          Weekly Plan
        </button>
      </div>

      {/* Quick Filters - Grouped by Category */}
      <div className="space-y-6 mb-6">
        {/* ⏱️ Duration */}
        <div className="p-4 rounded-xl bg-[#E6F3FF]">
          {" "}
          {/* Sky Frost */}
          <h3 className="font-semibold text-gray-800 mb-2">⏱ Duration</h3>
          <div className="flex flex-wrap gap-2">
            {quickFilters.slice(0, 2).map((filter) => (
              <button
                key={filter.label}
                onClick={() => fetchExercises(filter.query)}
                className="px-4 py-2 rounded-full bg-white text-sm hover:bg-blue-100 transition"
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* 💪 Muscle Groups */}
        <div className="p-4 rounded-xl bg-[#E6FFF3]">
          {" "}
          {/* Mint Whisper */}
          <h3 className="font-semibold text-gray-800 mb-2">💪 Muscle Groups</h3>
          <div className="flex flex-wrap gap-2">
            {quickFilters.slice(2, 6).map((filter) => (
              <button
                key={filter.label}
                onClick={() => fetchExercises(filter.query)}
                className="px-4 py-2 rounded-full bg-white text-sm hover:bg-green-100 transition"
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* ☀️ Daily Routines */}
        <div className="p-4 rounded-xl bg-[#FFFDE6]">
          {" "}
          {/* Lemon Veil */}
          <h3 className="font-semibold text-gray-800 mb-2">
            ☀️ Daily Routines
          </h3>
          <div className="flex flex-wrap gap-2">
            {quickFilters.slice(6, 9).map((filter) => (
              <button
                key={filter.label}
                onClick={() => fetchExercises(filter.query)}
                className="px-4 py-2 rounded-full bg-white text-sm hover:bg-yellow-100 transition"
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>

        {/* 🧠 Posture & Therapy */}
        <div className="p-4 rounded-xl bg-[#F4E6FF]">
          {" "}
          {/* Lavender Mist */}
          <h3 className="font-semibold text-gray-800 mb-2">
            🧠 Posture & Therapy
          </h3>
          <div className="flex flex-wrap gap-2">
            {quickFilters.slice(9).map((filter) => (
              <button
                key={filter.label}
                onClick={() => fetchExercises(filter.query)}
                className="px-4 py-2 rounded-full bg-white text-sm hover:bg-purple-100 transition"
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded">❌ {error}</div>
      )}

      {result && result.type === "weeklyPlan" && (
  <div className="space-y-6">
    {/* 🔹 One main Save button */}
    <button
      onClick={() => saveWeeklyPlanToLibrary(result.plan)}
      className="w-full bg-[#7B61FF] hover:bg-[#6B50E0] text-white font-semibold py-2 rounded-lg transition-colors duration-200"
    >
      💾 Save Weekly Plan
    </button>

    {/* 🔹 Render each day */}
    {result.plan.map((day, i) => {
      const url = typeof day.video === "string" ? day.video : null;
      if (!url) return null;

      const yt = extractYouTubeId(url);
      const vimeo = extractVimeoId(url);

      return (
        <div key={i} className="p-4 bg-gray-100 rounded-lg shadow">
          <h2 className="font-bold text-lg mb-2">{day.day}</h2>
          {day.name && <h3 className="font-semibold">{day.name}</h3>}
          {day.description && (
            <p className="text-sm text-gray-700 mb-2">{day.description}</p>
          )}

          <div>
            {yt && (
              <iframe
                className="w-full h-64 rounded-lg"
                src={`https://www.youtube.com/embed/${yt}`}
                allowFullScreen
              />
            )}
            {vimeo && (
              <iframe
                className="w-full h-64 rounded-lg"
                src={`https://player.vimeo.com/video/${vimeo}`}
                allowFullScreen
              />
            )}
            {url.match(/\.(mp4|webm)$/i) && (
              <video controls className="w-full h-64 rounded-lg">
                <source src={url} type={`video/${url.split(".").pop()}`} />
              </video>
            )}
            {!yt && !vimeo && !url.match(/\.(mp4|webm)$/i) && (
              <a
                href={url}
                target="_blank"
                className="text-blue-600 underline"
              >
                {url}
              </a>
            )}
          </div>
        </div>
      );
    })}
  </div>
)}


      {/* Results: Plan */}
      {result && result.type === "plan" && (
        <div className="space-y-3">
          {result.plan.map((exercise, i) => (
            <div key={i} className="p-3 bg-gray-100 rounded shadow">
              <h3 className="font-semibold">{exercise.name}</h3>
              <p className="text-sm text-gray-700">{exercise.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Results: Videos */}
      {result && result.type === "videos" && (
        <div className="space-y-4">
          {result.videos.length === 0 ? (
            <p className="text-gray-500">⚠️ No videos found.</p>
          ) : (
            result.videos.map((url, i) => {
              const yt = extractYouTubeId(url);
              const vimeo = extractVimeoId(url);

              return (
                <div key={i} className="space-y-2">
                  {yt && (
                    <iframe
                      className="w-full h-64 rounded-lg"
                      src={`https://www.youtube.com/embed/${yt}`}
                      allowFullScreen
                    />
                  )}
                  {vimeo && (
                    <iframe
                      className="w-full h-64 rounded-lg"
                      src={`https://player.vimeo.com/video/${vimeo}`}
                      allowFullScreen
                    />
                  )}
                  {url.match(/\.(mp4|webm)$/i) && (
                    <video controls className="w-full h-64 rounded-lg">
                      <source
                        src={url}
                        type={`video/${url.split(".").pop()}`}
                      />
                    </video>
                  )}
                  {!yt && !vimeo && !url.match(/\.(mp4|webm)$/i) && (
                    <a
                      href={url}
                      target="_blank"
                      className="text-blue-600 underline"
                    >
                      {url}
                    </a>
                  )}
                  <button
                    onClick={() => saveVideoToLibrary(url)}
                    className="px-3 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700"
                  >
                    + Save
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
