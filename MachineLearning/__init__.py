"""
Machine Learning Module for Exercise Tracking

This module provides AI-powered exercise tracking capabilities using YOLO pose estimation.
"""

__version__ = "1.0.0"
__author__ = "Zachary Stybel"

# Import main classes for easy access
try:
    from .models.advanced_bicep_tracker import AdvancedBicepTracker
    from .models.exercise_tracker import ExerciseTracker
except ImportError:
    # Handle relative import issues when running directly
    pass

__all__ = [
    'AdvancedBicepTracker',
    'ExerciseTracker'
]