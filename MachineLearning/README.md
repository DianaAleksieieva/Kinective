# 🤖 Machine Learning Module - Exercise Tracking

AI-powered exercise tracking system using YOLO pose estimation for real-time form analysis.

## 📁 Directory Structure

```
ml/
├── models/
│   ├── advanced_bicep_tracker.py    # Advanced bicep curl analysis
│   └── exercise_tracker.py          # Basic exercise tracking
├── tests/
│   ├── test_torch.py                # PyTorch installation test
│   └── test_yolo.py                 # YOLO detection test
├── utils/                           # Utility functions (future)
├── requirements.txt                 # ML dependencies
└── README.md                        # This file
```

## 🎯 Features

### Advanced Bicep Tracker (`advanced_bicep_tracker.py`)
- **Real-time Pose Detection**: YOLO11-pose for 17 keypoint tracking
- **Angle Analysis**: Precise arm angle calculations during bicep curls
- **Range of Motion**: Comprehensive ROM analysis and scoring
- **Form Feedback**: Real-time coaching and movement quality assessment
- **Data Export**: Session analytics exported to CSV
- **Multi-arm Support**: Track left, right, or both arms simultaneously

### Basic Exercise Tracker (`exercise_tracker.py`)
- Simplified pose detection and basic rep counting
- Foundation for more complex exercise types

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# From the ml directory
pip install -r requirements.txt
```

### 2. Test Installation
```bash
# Test PyTorch
python tests/test_torch.py

# Test YOLO detection
python tests/test_yolo.py
```

### 3. Run Exercise Tracker
```bash
# Basic tracker
python models/exercise_tracker.py

# Advanced bicep tracker
python models/advanced_bicep_tracker.py
```

## 🎮 Controls

- **`q`** - Quit application
- **`r`** - Reset current session
- **`s`** - Switch arms (left/right/both)
- **`a`** - Toggle analytics display
- **`e`** - Export session data

## 🔧 Configuration

### Camera Settings
```python
CAMERA_INDEX = 0  # Change for multiple cameras
CONFIDENCE_THRESHOLD = 0.5  # Detection confidence
```

### Analysis Parameters
```python
ANGLE_SMOOTHING = 5  # Movement smoothing (higher = smoother)
MIN_DETECTION_CONFIDENCE = 0.7  # Pose detection threshold
```

## 📊 Data Output

Session data includes:
- Timestamp for each frame
- Rep count and progression
- Arm angles (shoulder, elbow)
- Range of motion metrics
- Form quality scores
- Movement smoothness analysis

## 🔗 Integration

This ML module can be integrated into larger fitness applications by:
1. Importing the tracker classes
2. Using the pose detection utilities
3. Extending with additional exercise types
4. Connecting to databases or APIs

## 📋 Requirements

- Python 3.8+
- Webcam for real-time tracking
- ~50MB for YOLO model download (first run)
- OpenCV-compatible camera

## 🛠️ Development

### Adding New Exercises
1. Extend the base tracker class
2. Define exercise-specific keypoints
3. Implement movement analysis logic
4. Add form validation rules

### Model Updates
- YOLO models auto-download on first use
- Custom models can be specified in configuration
- Supports YOLO11n-pose, YOLO11s-pose, etc.

## 🧪 Testing

Run all tests:
```bash
python tests/test_torch.py && python tests/test_yolo.py
```

Individual component testing available for each model and utility function.