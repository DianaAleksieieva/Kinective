# bicep_adapter.py
# Adapter around Zach's advanced_bicep_tracker.py so we can call it per-frame.

import cv2
import numpy as np

# ==== IMPORT ZACH'S IMPLEMENTATION ====
# Make sure advanced_bicep_tracker.py has "if __name__ == '__main__':" around its CLI code
import advanced_bicep_tracker as z

_tracker = None

def init_tracker():
    """
    Call whatever one-time init Zach does (load YOLO, set params, etc.)
    and return an object/state you can reuse.
    """
    global _tracker
    # If Zach uses globals, we can just store a small state dict here.
    # Otherwise, create a small class instance and keep it in _tracker.
    _tracker = {
        "reps": 0,
        "state": "top",
        "side": "right",  # or 'left'
    }
    # If Zach exposes any init functions, call them here (e.g., z.init_model())
    # Example:
    if hasattr(z, "init_model"):
        z.init_model()
    return _tracker

def process_frame(frame_bgr: np.ndarray):
    """
    Given a BGR frame, run Zach's per-frame logic and return:
      - annotated_frame_bgr (np.ndarray)
      - metrics dict: {"reps": int, "state": "...", ...}
    """
    global _tracker
    if _tracker is None:
        init_tracker()

    # ---- CALL INTO ZACH'S LOGIC ----
    # You will need to map to whatever function in Zach's file does:
    #   - pose inference
    #   - HUD drawing (onto the frame)
    #   - rep counting / state update
    #
    # If Zach has a function like:
    #   annotated = z.update_and_draw(frame_bgr, _tracker)
    # use that here. Otherwise, copy the key code blocks into a helper
    # inside advanced_bicep_tracker.py and import it.

    if hasattr(z, "update_and_draw"):
        annotated, meta = z.update_and_draw(frame_bgr, _tracker)
        # meta should include reps/state. If not, build it from _tracker.
        metrics = {
            "reps": int(meta.get("reps", _tracker.get("reps", 0))),
            "state": str(meta.get("state", _tracker.get("state", "top"))),
        }
        return annotated, metrics

    # --- Fallback (no helper yet): just return the frame ---
    return frame_bgr, {
        "reps": int(_tracker.get("reps", 0)),
        "state": str(_tracker.get("state", "top")),
    }

def handle_command(cmd: str, **kwargs):
    """Optional: let the web app reset reps or switch arm."""
    global _tracker
    if _tracker is None:
        init_tracker()
    if cmd == "reset":
        _tracker["reps"] = 0
    elif cmd == "side":
        side = kwargs.get("side", "right")
        _tracker["side"] = side
    return {"ok": True, "state": _tracker}
