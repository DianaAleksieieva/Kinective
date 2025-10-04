"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function NavBar() {
  const router = useRouter();

  return (
    <nav className="flex justify-between items-center px-4 py-3 bg-purple-900/70 shadow-lg">
      <Link
        href="/"
        className="text-neonGreen font-bold text-lg hover:underline"
      >
        🏠 Home
      </Link>

      <button
        onClick={() => router.back()}
        className="text-neonGreen hover:underline"
      >
        ⬅ Back
      </button>
    </nav>
  );
}
