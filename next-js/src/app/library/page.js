"use client";
import { useState } from "react";

const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function LibraryPage() {
  const [videos, setVideos] = useState(
    daysOfWeek.map((day) => ({
      day,
      watched: false,
      removed: false,
      url: "https://www.w3schools.com/html/mov_bbb.mp4", // sample video
    }))
  );

  // ✅ Toggle watched state
  const toggleWatched = (index) => {
    const updated = [...videos];
    updated[index].watched = !updated[index].watched;
    setVideos(updated);
  };

  // ❌ Remove video
  const removeVideo = (index) => {
    const updated = [...videos];
    updated[index].removed = true;
    setVideos(updated);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-700 via-purple-800 to-purple-900 text-neonGreen p-8">
      <h1 className="text-4xl font-extrabold text-center mb-8">📚 Weekly Video Library</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video, index) => (
          <div
            key={video.day}
            className="bg-purple-900/80 p-4 rounded-xl shadow-lg flex flex-col items-center"
          >
            {/* Day Title */}
            <h2 className="text-xl font-bold mb-2">{video.day}</h2>

            {/* Video or Removed Notice */}
            {!video.removed ? (
              <>
                <video
                  src={video.url}
                  controls
                  className="w-full rounded-lg mb-3"
                />
                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={() => toggleWatched(index)}
                    className={`px-3 py-1 rounded-lg font-semibold ${
                      video.watched
                        ? "bg-green-500 text-white"
                        : "bg-neonGreen text-purple-900"
                    }`}
                  >
                    {video.watched ? "✅ Watched" : "Mark Watched"}
                  </button>
                  <button
                    onClick={() => removeVideo(index)}
                    className="px-3 py-1 rounded-lg bg-red-600 text-white font-semibold"
                  >
                    ❌ Remove
                  </button>
                </div>
              </>
            ) : (
              <p className="text-red-400 italic">Video removed ❌</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
