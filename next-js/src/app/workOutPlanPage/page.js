"use client";
import { useState } from "react";
import { doc, setDoc, arrayUnion } from "firebase/firestore";
import { db } from "@/lib/firebase"; 

export default function WorkOutPlanPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
    { label: "< 10 min", query: "quick 10 min workout exercise video" },
    { label: "10–20 min", query: "20 min workout exercise video" },
    { label: "Arms", query: "arm exercise video" },
    { label: "Biceps", query: "bicep exercise workout video" },
    { label: "Legs", query: "leg workout exercise video" },
    { label: "Core", query: "core strengthening exercise video" },
    { label: "Morning", query: "morning stretch exercise video" },
    { label: "Evening Stretch", query: "evening stretching routine video" },
    { label: "Cardio", query: "cardio workout exercise video" },
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
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
        >
          Search
        </button>
        <button
          onClick={() => fetchWeeklyPlan(query)}
          className="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700"
        >
          Weekly Plan
        </button>
      </div>

      {/* Quick Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        {quickFilters.map((filter) => (
          <button
            key={filter.label}
            onClick={() => fetchExercises(filter.query)}
            className="px-4 py-2 rounded-full bg-gray-200 text-sm hover:bg-gray-300"
          >
            {filter.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}
      {error && <div className="p-3 bg-red-100 text-red-700 rounded">❌ {error}</div>}

      {/* Results: Weekly Plan */}
      {result && result.type === "weeklyPlan" && (
        <div className="space-y-6">
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
                    <a href={url} target="_blank" className="text-blue-600 underline">
                      {url}
                    </a>
                  )}
                </div>

                <button
                  onClick={() => saveVideoToLibrary(url)}
                  className="mt-2 px-3 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700"
                >
                  + Save
                </button>
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
                      <source src={url} type={`video/${url.split(".").pop()}`} />
                    </video>
                  )}
                  {!yt && !vimeo && !url.match(/\.(mp4|webm)$/i) && (
                    <a href={url} target="_blank" className="text-blue-600 underline">
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