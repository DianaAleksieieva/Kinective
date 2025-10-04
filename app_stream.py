# app_stream.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import cv2, time

from bicep_adapter import init_tracker, process_frame, handle_command  # <-- NEW

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# ---------- camera ----------
def open_camera(preferred_width=1280, preferred_height=720, preferred_fps=30):
    prefs = [(0, cv2.CAP_AVFOUNDATION), (1, cv2.CAP_AVFOUNDATION), (0, cv2.CAP_ANY)]
    for idx, backend in prefs:
        cap = cv2.VideoCapture(idx, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, preferred_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, preferred_height)
            cap.set(cv2.CAP_PROP_FPS, preferred_fps)
            ok, _ = cap.read()
            if ok:
                print(f"✅ Camera opened (index={idx}, backend={backend})")
                return cap
            cap.release()
    raise RuntimeError("❌ Could not open any camera. Check macOS permissions.")

cap = open_camera()
_tracker_state = init_tracker()     # <-- initialize Zach’s tracker
latest_metrics = {"reps": 0, "state": "top"}

def gen():
    global latest_metrics
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.02)
            continue

        # Call Zach’s per-frame logic (draw HUD + update metrics)
        annotated, metrics = process_frame(frame)
        latest_metrics = metrics or latest_metrics

        # Encode as JPEG chunk
        ret, jpg = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpg.tobytes() +
            b"\r\n"
        )

# ---------- routes ----------
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html><body style="font-family:system-ui; margin:24px">
      <h2>Kinective local stream (Bicep)</h2>
      <img src="/video_feed" style="max-width: 100%; border-radius:12px; border:1px solid #ddd"/>
      <p>Try <a href="/metrics">/metrics</a> for JSON.</p>
      <p><a href="/cmd/reset">/cmd/reset</a> • switch side:
         <a href="/cmd/side?side=left">left</a> |
         <a href="/cmd/side?side=right">right</a></p>
    </body></html>
    """

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/metrics")
def metrics():
    return JSONResponse(latest_metrics)

@app.get("/cmd/{name}")
def cmd(name: str, side: str | None = None):
    # optional remote control: reset reps / switch arm
    if name == "reset":
        handle_command("reset")
    elif name == "side" and side in {"left", "right"}:
        handle_command("side", side=side)
    return {"ok": True}
