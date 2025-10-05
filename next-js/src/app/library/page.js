"use client";
import { useState, useEffect } from "react";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function LibraryPage() {
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    async function fetchVideos() {
      try {
        const userRef = doc(db, "users", "default");
        const snap = await getDoc(userRef);

        if (snap.exists()) {
          const data = snap.data();
          console.log("📦 Raw Firestore data:", data.library);

          let parsed = [];
          if (typeof data.library === "string") {
            try {
              parsed = JSON.parse(data.library);
              console.log("✅ Parsed library:", parsed);
            } catch (err) {
              console.error("❌ Failed to parse library string:", err);
            }
          } else if (Array.isArray(data.library)) {
            parsed = data.library;
            console.log("✅ Library already array:", parsed);
          }

          parsed = parsed.filter((v) => v && v.trim() !== "");
          console.log("🎯 Final filtered library:", parsed);

          setVideos(parsed);
        }
      } catch (err) {
        console.error("❌ Error fetching library:", err);
      }
    }
    fetchVideos();
  }, []);

  const [watched, setWatched] = useState({});
  const toggleWatched = (url) => {
    setWatched((prev) => ({ ...prev, [url]: !prev[url] }));
  };

  const removeVideo = async (url) => {
    try {
      const updated = videos.filter((v) => v !== url);
      setVideos(updated);

      const userRef = doc(db, "users", "default");
      await updateDoc(userRef, { library: JSON.stringify(updated) });

      console.log("🗑 Removed from Firestore:", url);
      console.log("📦 Updated library after removal:", updated);
    } catch (err) {
      console.error("❌ Error removing video:", err);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black p-8">
      <h1 className="text-4xl font-extrabold text-center mb-8">📚 Video Library</h1>

      {videos.length === 0 ? (
        <p className="text-center text-gray-600">No videos in your library yet 🎥</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((url) => (
            <div
              key={url}
              className="bg-gray-100 p-4 rounded-xl shadow-lg flex flex-col items-center"
            >
              {/* 🎥 Video */}
              {url.includes("youtube.com") || url.includes("youtu.be") ? (
                <iframe
                  src={url.replace("watch?v=", "embed/")}
                  className="w-full aspect-video rounded-lg mb-3"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              ) : url.includes("vimeo.com") ? (
                <iframe
                  src={url}
                  className="w-full aspect-video rounded-lg mb-3"
                  allow="autoplay; fullscreen; picture-in-picture"
                  allowFullScreen
                ></iframe>
              ) : (
                <video src={url} controls className="w-full rounded-lg mb-3" />
              )}

              {/* Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => toggleWatched(url)}
                  className={`px-3 py-1 rounded-lg font-semibold ${
                    watched[url]
                      ? "bg-green-500 text-white"
                      : "bg-green-300 text-black"
                  }`}
                >
                  {watched[url] ? "✅ Watched" : "Mark Watched"}
                </button>

                <button
                  onClick={() => removeVideo(url)}
                  className="px-3 py-1 rounded-lg bg-red-600 text-white font-semibold"
                >
                  ❌ Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
