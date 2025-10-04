"use client";
import { useEffect, useRef } from "react";

export default function SquatsPage() {
  const videoRef = useRef(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch((err) => {
            if (err.name !== "AbortError") {
              console.error("Video playback error:", err);
            }
          });
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          alert("Camera permission required to use this feature.");
          console.error(err);
        }
      }
    };

    startCamera();

    return () => {
      const stream = videoRef.current?.srcObject;
      const tracks = stream?.getTracks();
      tracks?.forEach((track) => track.stop());
    };
  }, []);

  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-black">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />
      <h1 className="absolute top-5 text-3xl font-bold text-white bg-purple-700/70 px-4 py-2 rounded-xl">
        🦵 Squats Mode
      </h1>
    </div>
  );
}
