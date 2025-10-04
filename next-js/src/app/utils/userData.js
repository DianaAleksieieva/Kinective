// src/utils/userData.js
const KEY = "kinectiveUserData";

// Load data
export function getUserData() {
  if (typeof window === "undefined") return { workouts: [] };
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : { workouts: [] };
  } catch {
    return { workouts: [] };
  }
}

// Save data
export function saveUserData(data) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(data));
}

// Log a workout for a day (defaults to today)
export function logWorkout(type = "General", duration = 30, date = new Date()) {
  const data = getUserData();

  // normalize to YYYY-MM-DD (no time)
  const day = new Date(date);
  day.setHours(0, 0, 0, 0);
  const iso = day.toISOString().slice(0, 10);

  const entry = { date: iso, type, duration: Number(duration) || 0 };
  const idx = data.workouts.findIndex(w => w.date === iso);

  if (idx > -1) data.workouts[idx] = entry; // replace same-day entry
  else data.workouts.push(entry);

  saveUserData(data);
  return entry;
}
