export default function ExercisePage() {
  return (
    <div className="p-6">
      <h2 className="text-3xl font-bold text-neonPurple mb-4 text-center">Exercise Tracker</h2>
      <p className="text-base text-neonGreen mb-6 text-center">
        Track your workouts, count reps, and stay consistent!
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="p-4 bg-black border border-neonPurple rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-neonGreen mb-2">🏋️ Strength</h3>
          <p className="text-sm">Log squats, push-ups, deadlifts and more.</p>
        </div>
        <div className="p-4 bg-black border border-neonGreen rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-neonPurple mb-2">🚴 Cardio</h3>
          <p className="text-sm">Track running, cycling, or rowing sessions.</p>
        </div>
        <div className="p-4 bg-black border border-neonPurple rounded-xl shadow-md">
          <h3 className="text-xl font-semibold text-neonGreen mb-2">🧘 Flexibility</h3>
          <p className="text-sm">Yoga, stretching, and recovery exercises.</p>
        </div>
      </div>
    </div>
  );
}
