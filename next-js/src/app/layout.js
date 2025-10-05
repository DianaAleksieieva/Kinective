import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Kinective Fitness App",
  description: "Your purple & neon green fitness companion 💪",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
     <body className="bg-gradient-to-b from-purple-700 via-purple-800 to-purple-900 min-h-screen flex flex-col">

        {/* 🧭 Top Navigation Bar */}
        <nav className="flex flex-wrap justify-center sm:justify-between items-center px-4 py-3 bg-purple-900/70 shadow-lg gap-3 text-white">
          {/* Logo / Home Button */}
          <Link href="/" className="flex items-center gap-2">
            <img
              src="/logo-k.png"
              alt="Kinective Logo"
              className="w-10 h-10 rounded-full"
            />
            <span className="font-extrabold text-xl tracking-wide ">
              Kinective
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex flex-wrap gap-3">
            <Link
              href="/exercise"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition  text-white"
            >
              🏋 Exercise
            </Link>

            <Link
              href="/workOutPlanPage"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition  text-white"
            >
              📝 Planning
            </Link>

            <Link
              href="/profile"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition  text-white"
            >
              👤 Profile
            </Link>

            {/* <Link
              href="/physical-therapy"
              className="px-3 py-1 bg-neonGreen text-purple-900 font-semibold rounded-lg hover:scale-105 transition  text-white"
            >
              🧠 Physical Therapy
            </Link> */}
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
