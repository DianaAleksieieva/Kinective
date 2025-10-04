// lib/langChainLogic.js
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

// 🔹 Gemini setup
const model = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash",
  temperature: 0.4,
  apiKey: process.env.GEMINI_API_KEY,
});

function normalizeQuery(userQuery) {
  const q = userQuery.trim().toLowerCase();

  // If user just types "back pain", "arms", "legs" → expand to exercise video search
  const fitnessContext = [
    "exercise",
    "workout",
    "fitness",
    "stretch",
    "rehab",
    "training",
  ];

  // If query doesn’t already mention exercise context → inject it
  const hasFitnessWord = fitnessContext.some((word) => q.includes(word));
  if (!hasFitnessWord) {
    return `${q} exercise workout video`;
  }

  return `${q} workout exercise fitness training stretch video`;
}

// 🔹 Tavily direct fetch
async function tavilySearch(query) {
  const response = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.TAVILY_API_KEY}`,
    },
    body: JSON.stringify({
      query: `${query} site:youtube.com OR site:vimeo.com OR site:dailymotion.com OR site:tiktok.com`,
      max_results: 10,
    }),
  });

  if (!response.ok) return [];
  const data = await response.json();

  const urls = (data.results || []).map((r) => r.url);

  // ✅ Step 1: Directly usable links
  const isDirectVideo = (url) =>
    url.includes("youtube.com/watch?v=") ||
    url.includes("youtube.com/shorts/") ||
    url.includes("youtu.be/") ||
    url.match(/\.(mp4|webm)$/i);

  const directVideos = urls.filter(isDirectVideo);

  // ✅ Step 2: Try extracting from page if not direct
  const extracted = await Promise.all(
    urls.map(async (url) => {
      if (isDirectVideo(url)) return null;
      return await extractVideoFromPage(url);
    })
  );

  return [...directVideos, ...extracted.filter(Boolean)];
}
async function extractVideoFromPage(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const html = await res.text();

    // ✅ Match common video patterns
    const videoRegex = /(https?:\/\/[^"'\s]+(?:\.mp4|\.webm))/i;
    const ytRegex = /(https?:\/\/www\.youtube\.com\/watch\?v=[\w-]{11})/i;

    const match = html.match(videoRegex) || html.match(ytRegex);
    return match ? match[0] : null;
  } catch {
    return null;
  }
}

export async function getExercisePlan(userQuery) {
  const normalized = normalizeQuery(userQuery);
  console.log("🟢 Running getExercisePlan for:", normalized);

  try {
    // STEP 1: Tavily
    const videos = await tavilySearch(normalized);
    if (videos.length > 0) {
      console.log("🎥 Tavily found:", videos);
      return { type: "videos", videos };
    }

    // STEP 2: Gemini fallback
    const result = await model.invoke(`
    You are a strict JSON generator acting as a fitness video assistant.

    TASK:
    - Treat the query "${normalized}" as fitness-related (workout, exercise, stretch, or rehab).
    - Generate 5 workout exercises VIDEOS only.
    - Respond ONLY as JSON in this exact format:
    [
      { "name": "string", "description": "short tip", "video": "valid playable video url" }
    ]
    - "video" must be a real video link (YouTube/Vimeo/TikTok/Dailymotion/Instagram/.mp4/.webm).
    - Never return articles, blogs, or PDFs.
    - Do NOT invent YouTube video links. Use only existing playable links.
    - If no valid links exist, return an empty array.
    `);

    let text = typeof result.content === "string" ? result.content.trim() : "";
    if (text.startsWith("```")) {
      text = text.replace(/```json|```/g, "").trim();
    }

    let parsed = [];
    try {
      parsed = JSON.parse(text);
    } catch (err) {
      console.warn("⚠️ Gemini JSON parse failed:", err.message);
    }

    return { type: "plan", plan: parsed };
  } catch (err) {
    console.error("❌ getExercisePlan failed:", err);
    return { type: "error", error: err.message || "Unknown error" };
  }
}
