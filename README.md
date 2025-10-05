🧠 Kinective

Kinective is an AI-powered fitness assistant that uses YOLO pose estimation and computer vision to track your form, count reps, and provide real-time feedback through a live camera feed. It helps users exercise confidently and safely without needing a personal trainer.

🚀 Setup
# Clone the repository
git clone https://github.com/<your-username>/Kinective.git
cd Kinective

# Install dependencies
pip install -r machine-learning/requirements.txt
pip install -r flask-backend/requirements.txt

# Test YOLO and OpenCV setup
python machine-learning/tests/test_yolo.py
python machine-learning/tests/test_cv.py

# Run the Flask server
cd flask-backend
python app.py


Visit http://127.0.0.1:5000/
 in your browser to start your AI workout session.
