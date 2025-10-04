export default function Home() {
  const currentYear = new Date().getFullYear();

  return (
    <div className="flex flex-col items-center justify-center text-center gap-6 w-full max-w-md min-h-screen pt-12 pb-8 px-6">
      {/* 🌀 Title */}
      <h1 className="text-5xl font-extrabold text-neonGreen drop-shadow-[0_0_8px_#39FF14]">
        Kinective
      </h1>

      {/* ✨ Subtitle */}
      <p className="text-neonGreen/90 text-lg mb-4">
        Your ultimate fitness hub 💪 Stay active, stay connected.
      </p>

      {/* 🧭 Navigation Buttons */}
      <div className="flex flex-col gap-4 w-full">
        <a
          href="/exercise"
          className="p-4 rounded-xl bg-neonGreen text-purple-900 font-bold shadow hover:scale-105 transition"
        >
          🏋 Exercise
        </a>

        <a
          href="/planning"
          className="p-4 rounded-xl bg-neonGreen text-purple-900 font-bold shadow hover:scale-105 transition"
        >
          📝 Planning
        </a>

        <a
          href="/profile"
          className="p-4 rounded-xl bg-neonGreen text-purple-900 font-bold shadow hover:scale-105 transition"
        >
          👤 Profile
        </a>

        <a
          href="/history"
          className="p-4 rounded-xl bg-neonGreen text-purple-900 font-bold shadow hover:scale-105 transition"
        >
          📅 History
        </a>

        {/* 🆕 Physical Therapy Button */}
        <a
          href="/physical-therapy"
          className="p-4 rounded-xl bg-neonGreen text-purple-900 font-bold shadow hover:scale-105 transition"
        >
          🧠 Physical Therapy
        </a>
      </div>

      {/* 📝 Footer */}
      <footer className="mt-auto pt-10 text-sm text-neonGreen/70">
        &copy; {currentYear} Kinective. All rights reserved.
      </footer>
    </div>
  );
}
