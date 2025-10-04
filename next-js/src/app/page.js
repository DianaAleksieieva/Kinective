export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <h1 className="text-4xl font-bold text-neonGreen mb-4">
        Welcome to VitaBuddy
      </h1>
      <p className="text-base text-neonPurple mb-6">
        Your AI-powered buddy for a healthier lifestyle 💪
      </p>

      <div className="flex flex-col gap-4 w-full max-w-xs">
        <a
          href="/exercise"
          className="w-full px-6 py-3 rounded-xl bg-neonGreen text-black font-semibold hover:bg-neonPurple hover:text-white transition text-center"
        >
          Exercise
        </a>
        <a
          href="/food"
          className="w-full px-6 py-3 rounded-xl bg-neonPurple text-white font-semibold hover:bg-neonGreen hover:text-black transition text-center"
        >
          Food
        </a>
      </div>
    </div>
  );
}
