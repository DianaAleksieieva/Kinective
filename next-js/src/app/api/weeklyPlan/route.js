import { getWeeklyPlan } from "@/lib/langChainLogic";

export async function POST(req) {
  try {
    const { query } = await req.json();
    console.log("🔎 Weekly Plan query received:", query);

    const result = await getWeeklyPlan(query || "full body workout");
    return Response.json(result);
  } catch (err) {
    console.error("❌ Weekly Plan API error:", err);
    return Response.json(
      { error: err.message || "Unknown error" },
      { status: 500 }
    );
  }
}
