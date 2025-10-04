#!/usr/bin/env python3
# Robust YOLOv8 Pose live demo (squat-focused) with loud HUD/debug

import os, sys, csv, argparse
from collections import deque
from typing import Tuple, Optional
import cv2, numpy as np, torch
from ultralytics import YOLO

# ---------- math helpers ----------
def angle(a: Tuple[float,float], b: Tuple[float,float], c: Tuple[float,float]) -> float:
    a,b,c = np.asarray(a,float), np.asarray(b,float), np.asarray(c,float)
    v1, v2 = a-b, c-b
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-8 or n2 < 1e-8: return 0.0
    d = (v1 @ v2) / (n1*n2)
    return float(np.degrees(np.arccos(np.clip(d, -1.0, 1.0))))

def torso_angle(shoulder, hip) -> float:
    v = np.asarray(shoulder,float) - np.asarray(hip,float)
    vu = np.array([0.0, -1.0])
    nv = np.linalg.norm(v)
    if nv < 1e-8: return 0.0
    d = float(v @ vu) / (nv * np.linalg.norm(vu))
    return float(np.degrees(np.arccos(np.clip(d, -1.0, 1.0))))

def signed_valgus_proxy(hip,knee,ankle) -> float:
    h,k,a = np.asarray(hip,float), np.asarray(knee,float), np.asarray(ankle,float)
    v = a - h; u = k - h; nv = np.linalg.norm(v)
    if nv < 1e-8: return 0.0
    cross_z = v[0]*u[1] - v[1]*u[0]
    return float(cross_z / (nv + 1e-8))

class EMA:
    def __init__(self, alpha: float = 0.35):
        self.alpha = float(alpha); self._v: Optional[float] = None
    def update(self, x: float) -> float:
        x = float(x)
        self._v = x if self._v is None else (self.alpha*x + (1.0-self.alpha)*self._v)
        return self._v
    @property
    def value(self): return self._v

# ---------- args ----------
def parse_args():
    p = argparse.ArgumentParser("YOLOv8 Pose live coach (squats)")
    p.add_argument("--model", default="yolov8n-pose.pt")
    p.add_argument("--source", type=int, default=0)
    p.add_argument("--imgsz", type=int, default=448)
    p.add_argument("--mirror", action="store_true")
    p.add_argument("--nosave", action="store_true")
    p.add_argument("--out", default="session_annotated.mp4")
    p.add_argument("--csv", default="", help="Per-rep CSV path; empty disables")
    p.add_argument("--alpha", type=float, default=0.35)
    # thresholds (tuned lenient for visibility)
    p.add_argument("--down_thr", type=float, default=110.0)
    p.add_argument("--up_thr", type=float, default=160.0)
    p.add_argument("--min_hold", type=int, default=3)
    p.add_argument("--min_rep_frames", type=int, default=10)
    p.add_argument("--torso_warn", type=float, default=30.0)
    p.add_argument("--valgus_thr", type=float, default=12.0)
    p.add_argument("--hip_drop_frac", type=float, default=0.03)
    p.add_argument("--feet_stab", type=float, default=0.04)
    p.add_argument("--kp_conf", type=float, default=0.30)  # more lenient so HUD shows
    return p.parse_args()

# ---------- main ----------
def main():
    args = parse_args()
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = YOLO(args.model).to(device)

    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {args.source}.", file=sys.stderr); sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  or 1280
    h  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

    out = None
    if not args.nosave:
        out = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w,h))

    # state & buffers
    ema_knee = EMA(args.alpha); ema_torso = EMA(args.alpha)
    knee_hist = deque(maxlen=int(fps*8)); torso_hist = deque(maxlen=int(fps*8))
    hip_y_hist = deque(maxlen=int(fps*4)); ank_hist = deque(maxlen=int(fps*4))
    state, reps, hold, rep_frames = "top", 0, 0, 0
    rep_buf = []

    writer = None; csv_f = None
    if args.csv:
        new_file = not os.path.exists(args.csv)
        csv_f = open(args.csv, "a", newline="")
        writer = csv.DictWriter(csv_f, fieldnames=["knee_min","knee_max","knee_rom","torso_mean","torso_std","valgus_max","label"])
        if new_file: writer.writeheader()

    print("Press 'q' to quit, 'r' to reset reps.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            if args.mirror: frame = cv2.flip(frame, 1)

            r0 = model.predict(source=frame, imgsz=args.imgsz, device=device, verbose=False)[0]
            annotated = r0.plot(boxes=False, labels=False)

            dets = int(r0.boxes.shape[0]) if getattr(r0, "boxes", None) is not None else 0
            # Top bar: detections & fps-ish info
            cv2.putText(annotated, f"Detections: {dets}", (18, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50,255,255), 2)

            if r0.keypoints is None or len(r0.keypoints) == 0:
                cv2.putText(annotated, "NO KEYPOINTS", (18, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)
                if out is not None: out.write(annotated)
                cv2.imshow("YOLO Pose - Live", annotated)
                if cv2.waitKey(1) & 0xFF in (27, ord('q')): break
                continue

            kps  = r0.keypoints.xy[0].cpu().numpy()
            conf = r0.keypoints.conf[0].cpu().numpy() if getattr(r0.keypoints,"conf",None) is not None else None

            # indices
            LSHO,RSHO = kps[5],kps[6]; LHIP,RHIP = kps[11],kps[12]
            LKNEE,RKNEE = kps[13],kps[14]; LANK,RANK = kps[15],kps[16]

            # confidence gate (only if conf available AND kp_conf>0)
            if conf is not None and args.kp_conf > 0:
                needed = [5,6,11,12,13,14,15,16]
                low = [i for i in needed if conf[i] < args.kp_conf]
                if low:
                    cv2.putText(annotated, f"LOW CONF: {low}", (18, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
                    if out is not None: out.write(annotated)
                    cv2.imshow("YOLO Pose - Live", annotated)
                    if cv2.waitKey(1) & 0xFF in (27, ord('q')): break
                    continue

            # angles
            lk = angle(LHIP, LKNEE, LANK); rk = angle(RHIP, RKNEE, RANK)
            knee = min(lk, rk)
            t_left = torso_angle(LSHO, LHIP); t_right = torso_angle(RSHO, RHIP)
            torso = 0.5*(t_left + t_right)
            vk_l = abs(signed_valgus_proxy(LHIP, LKNEE, LANK))
            vk_r = abs(signed_valgus_proxy(RHIP, RKNEE, RANK))
            valgus = max(vk_l, vk_r)

            # scale + midpoints
            mid_sho = ((LSHO[0]+RSHO[0])*0.5, (LSHO[1]+RSHO[1])*0.5)
            mid_hip = ((LHIP[0]+RHIP[0])*0.5, (LHIP[1]+RHIP[1])*0.5)
            mid_ank = ((LANK[0]+RANK[0])*0.5, (LANK[1]+RANK[1])*0.5)
            scale = max(1.0, np.linalg.norm(np.array(mid_sho) - np.array(mid_hip)))

            # histories + smoothing
            hip_y_hist.append(mid_hip[1]); ank_hist.append(mid_ank)
            k_s = ema_knee.update(knee); t_s = ema_torso.update(torso)
            knee_hist.append(k_s); torso_hist.append(t_s)
            rep_buf.append((k_s, t_s, valgus))
            if len(rep_buf) > int(fps*12): rep_buf.pop(0)

            # gates
            ank_arr = np.array(ank_hist, float)
            ank_dx = (ank_arr[:,0].max() - ank_arr[:,0].min()) / scale
            ank_dy = (ank_arr[:,1].max() - ank_arr[:,1].min()) / scale
            feet_stable = (ank_dx < args.feet_stab) and (ank_dy < args.feet_stab)

            hip_arr = np.array(hip_y_hist, float)
            hip_drop = (hip_arr.max() - hip_arr.min()) / scale
            enough_drop = hip_drop > args.hip_drop_frac

            # FSM
            if state == "top":
                rep_frames = 0
                if (k_s < args.down_thr) and feet_stable:
                    state, hold = "down", 0
            elif state == "down":
                rep_frames += 1; hold += 1
                if (k_s > args.up_thr) and (hold > args.min_hold) and feet_stable and enough_drop and (rep_frames >= args.min_rep_frames):
                    reps += 1; state = "top"
                    if writer and len(rep_buf) > 5:
                        arr = np.array(rep_buf,float)
                        knee_min, knee_max = float(arr[:,0].min()), float(arr[:,0].max())
                        writer.writerow({
                            "knee_min": knee_min, "knee_max": knee_max, "knee_rom": knee_max-knee_min,
                            "torso_mean": float(arr[:,1].mean()), "torso_std": float(arr[:,1].std()),
                            "valgus_max": float(np.abs(arr[:,2]).max()), "label": 1
                        })
                    rep_buf.clear()

            # HUD main
            depth_ok   = (k_s < args.down_thr)
            valgus_bad = (valgus > args.valgus_thr)
            torso_bad  = (t_s > args.torso_warn)
            color = (0,255,0) if (depth_ok and not valgus_bad and not torso_bad) else (0,165,255) if depth_ok else (0,0,255)

            cv2.putText(annotated, f"Knee angle: {k_s:5.1f} deg", (18, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
            cv2.putText(annotated, f"Reps: {reps} | State: {state}", (18, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            hint = "Go deeper" if not depth_ok else "Knees out" if valgus_bad else "Chest up" if torso_bad else ""
            if hint:
                cv2.putText(annotated, hint, (18, 154), cv2.FONT_HERSHEY_SIMPLEX, 0.95, color, 3)

            # Debug gates (so you *see* why it won’t count)
            dbg = [
                f"knee<{args.down_thr:.0f}: {k_s < args.down_thr}",
                f"feet_stable: {feet_stable} (dx={ank_dx:.3f}, dy={ank_dy:.3f})",
                f"hip_drop>{args.hip_drop_frac:.2f}: {enough_drop} (drop={hip_drop:.3f})",
                f"dur>={args.min_rep_frames}: {rep_frames >= args.min_rep_frames}",
            ]
            for i, txt in enumerate(dbg):
                cv2.putText(annotated, txt, (18, 186 + i*26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200), 2)

            if out is not None: out.write(annotated)
            cv2.imshow("YOLO Pose - Live", annotated)
            k = cv2.waitKey(1) & 0xFF
            if k in (27, ord('q')): break
            if k == ord('r'): reps, state, rep_buf[:] = 0, "top", []

    finally:
        cap.release()
        if out is not None: out.release()
        cv2.destroyAllWindows()
        try:
            if csv_f: csv_f.close()
        except Exception: pass
        if not args.nosave: print(f"Saved annotated video to '{args.out}'")
        print("Done.")

if __name__ == "__main__":
    main()
