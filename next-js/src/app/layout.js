import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Kinective Fitness App",
  description: "Your purple & neon green fitness companion 💪",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 min-h-screen flex flex-col">
        {/* 🧭 Top Navigation Bar */}
        <nav className="flex flex-wrap justify-center sm:justify-between items-center px-4 py-3 bg-purple-900/70 shadow-lg gap-3">
          {/* Logo / Home Button */}
          <Link href="/" className="flex items-center gap-2">
  <img
    src="/kinectivelogo.png"
    alt="Kinective Logo"
    className="w-8 h-8 rounded-full"
  />
  <span className="text-white font-extrabold text-xl tracking-wide">
    Kinective
  </span>
</Link>


          {/* Navigation Links */}
          <div className="flex flex-wrap gap-3">
            <Link
              href="/exercise"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition"
            >
              🏋 Exercise
            </Link>

            <Link
              href="/planning"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition"
            >
              📝 Planning
            </Link>

            <Link
              href="/profile"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition"
            >
              👤 Profile
            </Link>

            <Link
              href="/history"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition"
            >
              📅 History
            </Link>

            {/* 🆕 Physical Therapy Navigation */}
            <Link
              href="/physical-therapy"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition"
            >
              🧠 Physical Therapy
            </Link>
          </div>
        </nav>

        {/* 🌿 Page Content */}
        <main className="flex-grow flex flex-col items-center justify-start p-6">
          {children}
        </main>
      </body>
    </html>
  );
}
