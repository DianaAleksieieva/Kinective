/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neonGreen: "#39FF14",
        neonPurple: "#9D00FF",
      },
    },
  },
  plugins: [],
};
