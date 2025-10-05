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

async function isPlayableYouTubeUrl(url) {
  if (!/youtu(\.be|be\.com)/.test(url)) return true; // not YouTube → skip check
  try {
    const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`;
    const res = await fetch(oembedUrl, { method: "GET" });
    return res.ok; // 404 => removed/private
  } catch {
    return false;
  }
}

// 🔹 Weekly plan
export async function getWeeklyPlan(userQuery) {
  const normalized = normalizeQuery(userQuery);
  console.log("🟢 Running getWeeklyPlan for:", normalized);

  try {
    // STEP 1: Fetch from Tavily
    const videos = await tavilySearch(normalized);
    console.log("🎥 Tavily returned:", videos.length, "videos");

    // STEP 2: Filter only valid-looking links
    const validVideos = videos.filter(isValidVideoUrl);
    console.log("✅ Rough valid videos:", validVideos.length);

    // STEP 3: Shuffle and pick up to 7
    const shuffled = validVideos.sort(() => 0.5 - Math.random());
    const limited = shuffled.slice(0, Math.min(7, shuffled.length));

    // STEP 4: Build weekly plan (can be <7)
    const weeklyPlan = limited.map((video, i) => ({
      day: `Day ${i + 1}`,
      video,
      name: "Suggested workout",
      description: `Exercise video for ${normalized}`,
    }));

    // ✅ If 3+ valid videos found → return plan as-is
    if (weeklyPlan.length >= 3) {
      console.log(`✅ Returning ${weeklyPlan.length}-day plan from Tavily.`);
      return { type: "weeklyPlan", plan: weeklyPlan };
    }

    // ⚠️ If no valid videos or too few → Gemini fallback
    console.log("⚠️ Not enough valid videos, calling Gemini fallback…");
    const result = await model.invoke(`
You are a strict JSON generator acting as a fitness video assistant.

TASK:
- Treat the user query "${normalized}" as fitness-related (workout, stretch, rehab, training).
- Generate up to 7 days of workout videos if you can find **real video links**.
- Each item should include only one video per day.

FORMAT:
[
  { "day": "Day 1", "video": "valid playable url", "name": "string", "description": "short tip" },
  ...
]

RULES:
- "video" must be a real, playable link (YouTube, Vimeo, TikTok, Dailymotion, Instagram reels, or .mp4/.webm).
- Do NOT make up or fake URLs.
- No markdown, no explanations — only JSON.
`);

    let text = typeof result.content === "string" ? result.content.trim() : "";
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
      return { type: "weeklyPlan", plan: [] };
    }
  } catch (err) {
    console.error("❌ getWeeklyPlan failed:", err);
    return { type: "error", error: err.message || "Unknown error" };
  }
}
