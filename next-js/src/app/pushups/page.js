"use client";
import { useEffect, useRef } from "react";

export default function PushupsPage() {
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
    <div className="relative w-screen h-screen flex flex-col items-center justify-center bg-black overflow-hidden">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="absolute top-0 left-0 w-full h-full object-cover"
      />
      <h1 className="absolute top-5 text-3xl font-bold text-white bg-purple-700/70 px-4 py-2 rounded-xl">
        ✈ Push-ups Mode
      </h1>
    </div>
  );
}
