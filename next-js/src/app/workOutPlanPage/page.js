"use client";
import { useState } from "react";
import { doc, setDoc, updateDoc, arrayUnion } from "firebase/firestore";

import { db } from "@/lib/firebase"; 

export default function WorkOutPlanPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

// 🔹 Save video to Firebase (with debug logs)
async function saveVideoToLibrary(videoUrl) {
  console.log("🟢 Save button clicked for:", videoUrl);
  try {
    const userRef = doc(db, "users", "default");
    console.log("📌 Firestore doc reference:", userRef.path);

    await setDoc(
      userRef,
      { library: arrayUnion(videoUrl) },
      { merge: true } // ✅ will create if missing
    );

    console.log("✅ Successfully saved to Firestore:", videoUrl);
    alert("✅ Video saved to library!");
  } catch (err) {
    console.error("❌ Error saving video:", err);
    alert("Failed to save video.");
  }
}


  // 🔹 Extract YouTube ID
  function extractYouTubeId(url) {
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
    const match = url.match(/(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)/);
    return match ? match[1] : null;
  }

  // 🔹 Filter likely video links (no playlists/articles)
  function isLikelyVideo(url) {
    return (
      extractYouTubeId(url) ||
      extractVimeoId(url) ||
      url.match(/\.(mp4|webm)$/i) ||
      url.includes("tiktok.com/video") ||
      url.includes("dailymotion.com/video") ||
      url.includes("instagram.com/reel") ||
      url.includes("facebook.com/watch")
    );
  }

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

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      console.log("📦 Raw API Response:", data);

      setResult(data);
    } catch (err) {
      console.error("❌ Error fetching exercises:", err);
      setError(err.message);
    }

    setLoading(false);
  }

  // 🔹 Quick Filters with more specific queries
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

      {loading && <p className="text-gray-500">Loading exercises…</p>}
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded">
          ❌ Error: {error}
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
                  {/* YouTube */}
                  {yt && (
                    <div className="aspect-video">
                      <iframe
                        className="w-full h-64 rounded-lg shadow"
                        src={`https://www.youtube.com/embed/${yt}`}
                        title={`YouTube video ${i}`}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      ></iframe>
                    </div>
                  )}

                  {/* Vimeo */}
                  {vimeo && (
                    <div className="aspect-video">
                      <iframe
                        className="w-full h-64 rounded-lg shadow"
                        src={`https://player.vimeo.com/video/${vimeo}`}
                        title={`Vimeo video ${i}`}
                        frameBorder="0"
                        allow="autoplay; fullscreen; picture-in-picture"
                        allowFullScreen
                      ></iframe>
                    </div>
                  )}

                  {/* MP4/WebM */}
                  {url.match(/\.(mp4|webm)$/i) && (
                    <video controls className="w-full h-64 rounded-lg shadow">
                      <source src={url} type={`video/${url.split(".").pop()}`} />
                      Your browser does not support the video tag.
                    </video>
                  )}

                  {/* Fallback link */}
                  {!yt && !vimeo && !url.match(/\.(mp4|webm)$/i) && (
                    <div className="p-2 bg-gray-100 rounded shadow">
                      <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline break-all"
                      >
                        {url}
                      </a>
                    </div>
                  )}

                  {/* Save Button */}
                  <button
                    onClick={() => saveVideoToLibrary(url)}
                    className="px-3 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700"
                  >
                    + Save to Library
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
