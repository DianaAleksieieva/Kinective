"use client";
import Link from "next/link";

export default function ExercisePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center gap-6">
      <h1 className="text-4xl font-extrabold text-purple-800">🏋 Exercise Tracker</h1>
      <p className="text-gray-700">Choose a workout to get started and keep your streak alive!</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg w-full">
        {/* Arms */}
        <Link
          href="/arms"
          className="bg-purple-700 text-white font-semibold p-4 rounded-xl shadow hover:scale-105 transition"
        >
          💪 Arms
          <p className="text-sm opacity-80">
            Bicep curls, triceps, and upper body workouts.
          </p>
        </Link>

        {/* Squats */}
        <Link
          href="/squats"
          className="bg-purple-700 text-white font-semibold p-4 rounded-xl shadow hover:scale-105 transition"
        >
          🦵 Squats
          <p className="text-sm opacity-80">
            Perfect your squat form and track reps.
          </p>
        </Link>

        {/* Push-ups */}
        <Link
          href="/pushups"
          className="bg-purple-700 text-white font-semibold p-4 rounded-xl shadow hover:scale-105 transition md:col-span-2"
        >
          ✈ Push-ups
          <p className="text-sm opacity-80">
            Count your push-ups and build core strength.
          </p>
        </Link>
      </div>
    </div>
  );
}
