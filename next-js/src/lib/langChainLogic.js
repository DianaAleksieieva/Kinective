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
  const fitnessContext = [
    "exercise",
    "workout",
    "fitness",
    "stretch",
    "rehab",
    "training",
  ];
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
      max_results: 15,
    }),
  });

  if (!response.ok) return [];
  const data = await response.json();
  const urls = (data.results || []).map((r) => r.url);

  const isDirectVideo = (url) =>
    url.includes("youtube.com/watch?v=") ||
    url.includes("youtube.com/shorts/") ||
    url.includes("youtu.be/") ||
    url.match(/\.(mp4|webm)$/i);

  const directVideos = urls.filter(isDirectVideo);

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
    const videoRegex = /(https?:\/\/[^"'\s]+(?:\.mp4|\.webm))/i;
    const ytRegex = /(https?:\/\/www\.youtube\.com\/watch\?v=[\w-]{11})/i;
    const match = html.match(videoRegex) || html.match(ytRegex);
    return match ? match[0] : null;
  } catch {
    return null;
  }
}

// 🔹 Single plan
export async function getExercisePlan(userQuery) {
  const normalized = normalizeQuery(userQuery);
  console.log("🟢 Running getExercisePlan for:", normalized);

  try {
    const videos = await tavilySearch(normalized);
    if (videos.length > 0) {
      return { type: "videos", videos };
    }

    const result = await model.invoke(`
      You are a strict JSON generator acting as a fitness video assistant.
      TASK:
      - Treat the query "${normalized}" as fitness-related.
      - Generate 5 workout exercise VIDEOS only.
      - Respond ONLY as JSON array:
        [ { "name": "string", "description": "short tip", "video": "valid playable url" } ]
      - "video" must be a real video link (YouTube/Vimeo/TikTok/Dailymotion/Instagram/.mp4/.webm).
      - No blogs, no articles, no PDFs, no fake YouTube IDs.
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

// 🔹 Validate playable video URLs
function isValidVideoUrl(url) {
  if (!url || typeof url !== "string") return false;

  const patterns = [
    /youtube\.com\/watch\?v=/i,
    /youtube\.com\/shorts\//i,
    /youtu\.be\//i,
    /vimeo\.com\/\d+/i,
    /tiktok\.com\/video\//i,
    /dailymotion\.com\/video\//i,
    /instagram\.com\/reel\//i,
    /\.(mp4|webm)$/i,
  ];

  return patterns.some((p) => p.test(url));
}

// 🔹 Weekly plan
export async function getWeeklyPlan(userQuery) {
  const normalized = normalizeQuery(userQuery);
  console.log("🟢 Running getWeeklyPlan for:", normalized);

  try {
    // STEP 1: Fetch from Tavily
    const videos = await tavilySearch(normalized);
    console.log("🎥 Tavily returned:", videos.length, "videos");

    // Filter only valid playable links
    const validVideos = videos.filter(isValidVideoUrl);
    console.log("✅ Valid videos after filter:", validVideos.length);

    // Shuffle
    const shuffled = validVideos.sort(() => 0.5 - Math.random());

    // ✅ Build only as many days as we actually have
    const weeklyPlan = shuffled.slice(0, 7).map((video, i) => ({
      day: `Day ${i + 1}`,
      video,
      name: "Suggested workout",
      description: `Exercise video for ${normalized}`,
    }));

    // STEP 2: If fewer than 7 → fallback to Gemini
    if (weeklyPlan.length < 7) {
      console.log("⚠️ Not enough videos, calling Gemini fallback…");
      const result = await model.invoke(`
You are a strict JSON generator acting as a fitness video assistant.

TASK:
- Treat the user query "${normalized}" as fitness-related (workout, stretch, rehab, training).
- Generate a **7-day workout plan**.
- Each day must contain exactly 1 unique exercise video.
- Tailor the selection to match the query (e.g. if the user says "15 min full body", find 15 min full body videos).
- Respond ONLY as a valid JSON array of 7 objects in this exact format:
[
  { "day": "Day 1", "video": "valid playable url", "name": "string", "description": "short tip" },
  ...
  { "day": "Day 7", "video": "valid playable url", "name": "string", "description": "short tip" }
]

RULES:
- "video" must be a real, playable link (YouTube, Vimeo, TikTok, Dailymotion, Instagram reels, or .mp4/.webm).
- Each of the 7 videos must be unique (no repeats).
- Do NOT return articles, blogs, PDFs, or fake YouTube IDs.
- No extra text, no markdown, only the JSON array.
`);

      let text = typeof result.content === "string" ? result.content.trim() : "";
      console.log("📦 Raw Gemini output:", text);

      if (text.startsWith("```")) {
        text = text.replace(/```json|```/g, "").trim();
      }

      let parsed = [];
      try {
        parsed = JSON.parse(text);
        parsed = parsed.filter((d) => d && isValidVideoUrl(d.video));
        console.log("✅ Parsed Gemini weekly plan:", parsed);
        return { type: "weeklyPlan", plan: parsed };
      } catch (err) {
        console.warn("⚠️ Gemini JSON parse failed:", err.message);
        return { type: "weeklyPlan", plan: weeklyPlan };
      }
    }

    // Default return (valid Tavily normalized plan)
    console.log("✅ Returning Tavily weeklyPlan:", weeklyPlan);
    return { type: "weeklyPlan", plan: weeklyPlan };
  } catch (err) {
    console.error("❌ getWeeklyPlan failed:", err);
    return { type: "error", error: err.message || "Unknown error" };
  }
}
