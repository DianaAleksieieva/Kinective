export default function Home() {
  const currentYear = new Date().getFullYear();

  return (
    <div className="flex flex-col items-center justify-center text-center gap-8 w-full max-w-md min-h-screen pt-12 pb-8 px-6">
      {/* 🌀 Title */}
      <h1 className="text-6xl font-extrabold text-[#59168bb1]">
        Kinective
      </h1>
      {/* ✨ Subtitle */}
      <p className="text-neonGreen/90 text-lg mb-6">
        Plan smarter. Move better. Kinective helps you perfect every rep with real-time feedback.
      </p>

      {/* 🧭 Navigation Buttons */}
      <div className="flex flex-col gap-5 w-full">
        <a
          href="/exercise"
          className="py-5 bg-[#F4E6FF] px-4 text-xl rounded-xl bg-neonGreen text-black font-bold hover:scale-105 transition-transform shadow"
        >
          🏋 Exercise
          <div className="text-sm font-normal text-black/80 mt-1">
            Improve exercise technique
          </div>
        </a>

        <a
          href="/workOutPlanPage"
          className="py-5 bg-[#FFFDE6] text-xl px-4 rounded-xl bg-neonGreen text-black font-bold hover:scale-105 transition-transform shadow"
        >
          📝 Planning
          <div className="text-sm font-normal text-black/80 mt-1">
            Create your personalized weekly workout plan
          </div>
        </a>

        <a
          href="/profile"
          className="py-5 bg-[#E6FFF3] px-4 text-xl rounded-xl bg-neonGreen text-black font-bold hover:scale-105 transition-transform shadow"
        >
          👤 Profile
          <div className="text-sm font-normal text-black/80 mt-1">
            Access your saved workouts and track progress
          </div>
        </a>

        <a
          href="/library"
          className="py-5 bg-[#FFE6F7] text-xl px-4 rounded-xl bg-neonGreen text-black font-bold hover:scale-105 transition-transform shadow"
        >
          📹 Video Library 
          <div className="text-sm font-normal text-black/80 mt-1">
            Review your saved video and weekly plan
          </div>
        </a>

        {/* <a
          href="/physical-therapy"
          className="py-5 px-4 text-xl rounded-xl bg-neonGreen text-black font-bold hover:scale-105 transition-transform shadow"
        >
          🧠 Physical Therapy
          <div className="text-sm font-normal text-black/80 mt-1">
            Restore strength and mobility through guided therapy.
          </div>
        </a> */}
      </div>

      {/* 📝 Footer */}
      <footer className="mt-auto pt-10 text-sm text-neonGreen/70">
        &copy; {currentYear} Kinective. All rights reserved.
      </footer>
    </div>
  );
}
