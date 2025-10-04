# Advanced Configuration for Live Exercise Tracking
# Tune these parameters to improve your live results!

# === DETECTION SETTINGS ===
YOLO_CONFIDENCE = 0.7  # Higher = fewer false positives (0.5-0.9)
KEYPOINT_CONFIDENCE = 0.7  # Minimum confidence for individual keypoints
MIN_KEYPOINTS_REQUIRED = 6  # Minimum number of good keypoints needed

# === FILTERING & SMOOTHING ===
ANGLE_SMOOTHING_WINDOW = 5  # Frames to average (higher = smoother but slower response)
OUTLIER_REJECTION_THRESHOLD = 30  # Reject angles that differ by more than this from average

# === EXERCISE-SPECIFIC THRESHOLDS ===
PUSHUP_DOWN_ANGLE = 90  # Elbow angle for "down" position
PUSHUP_UP_ANGLE = 160   # Elbow angle for "up" position
PUSHUP_MIN_VALID_ANGLE = 60  # Reject angles below this (likely detection errors)

BICEP_CONTRACTED_ANGLE = 50  # Bicep curl "up" position
BICEP_EXTENDED_ANGLE = 160   # Bicep curl "down" position

# === FORM ANALYSIS ===
BODY_ALIGNMENT_WEIGHT = 0.4  # How much body alignment affects form score (0-1)
ANGLE_ACCURACY_WEIGHT = 0.6  # How much angle accuracy affects form score (0-1)

# === CAMERA & DISPLAY ===
CAMERA_INDEX = 0  # Which camera to use (0, 1, 2, etc.)
FRAME_WIDTH = 640  # Camera resolution width
FRAME_HEIGHT = 480  # Camera resolution height
MIRROR_CAMERA = True  # Flip camera horizontally

# === ADVANCED FILTERING ===
USE_TEMPORAL_FILTERING = True  # Enable time-based filtering
TEMPORAL_WINDOW = 10  # Frames to consider for temporal consistency
MIN_REP_DURATION = 1.0  # Minimum seconds between reps (prevents false counting)

# === CALIBRATION ===
AUTO_CALIBRATE = True  # Auto-adjust thresholds based on user's range
CALIBRATION_REPS = 3  # Number of reps to use for calibration