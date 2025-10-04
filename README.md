# VitaBuddy

## 🏗️ Project Structure

```
Kinective/
├── fast-api/                       # 🚀 Backend API
├── next-js/                        # 🌐 Frontend Web Application  
├── MachineLearning/                 # 🤖 AI & ML Module
│   ├── models/
│   │   ├── advanced_bicep_tracker.py  # Advanced exercise analysis
│   │   └── exercise_tracker.py        # Basic tracking
│   ├── tests/
│   │   ├── test_torch.py              # PyTorch tests
│   │   └── test_yolo.py               # YOLO tests
│   ├── utils/                         # ML utility functions
│   ├── requirements.txt               # ML dependencies
│   ├── README.md                      # ML documentation
│   └── __init__.py                    # Python module setup
├── advanced_bicep_tracker.py          # 🏋️ Main Exercise Tracker
└── README.md                          # This file
```

## 🚀 Quick Start

### Machine Learning Module
```bash
# Install ML dependencies
cd MachineLearning
pip install -r requirements.txt

# Test ML setup
python tests/test_torch.py
python tests/test_yolo.py

# Run exercise tracker
python ../advanced_bicep_tracker.py
```

## 🤖 ML Features

- **Real-time Pose Detection** using YOLO11-pose
- **Advanced Exercise Analysis** for bicep curls
- **Range of Motion** tracking and scoring
- **Form Quality Assessment** with real-time feedback
- **Session Data Export** for analytics