// app/api/exercise/route.js
import { getExercisePlan } from "@/lib/langChainLogic";

export async function POST(req) {
  try {
    const { query } = await req.json();
    console.log("🔎 Query received:", query);

    const result = await getExercisePlan(query || "quick workout");
    return Response.json(result);
  } catch (err) {
    console.error("❌ API error:", err);
    return Response.json(
      { error: err.message || "Unknown error" },
      { status: 500 }
    );
  }
}
