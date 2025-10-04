#!/usr/bin/env python3
"""
Advanced Analytics for Exercise Tracking
Weekly reports, progress trends, and insights
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List

class ExerciseAnalytics:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.data_file = f"user_progress_{user_id}.json"
        self.load_data()
    
    def load_data(self):
        """Load user exercise data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"session_history": []}
    
    def generate_weekly_report(self):
        """Generate comprehensive weekly report"""
        sessions = self.data.get('session_history', [])
        if not sessions:
            print("📊 No workout data available for analysis")
            return
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(sessions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        week_data = df[df['date'] >= start_date]
        
        if week_data.empty:
            print("📊 No workouts in the past 7 days")
            return
        
        # Calculate metrics
        total_reps = week_data['total_reps'].sum()
        total_sessions = len(week_data)
        avg_form_score = week_data['avg_form_score'].mean()
        total_calories = week_data['calories_burned'].sum()
        total_duration = week_data['duration_minutes'].sum()
        
        # Exercise variety
        exercises_this_week = week_data['exercise_type'].unique()
        
        print("📊 WEEKLY REPORT")
        print("="*50)
        print(f"📅 Period: {start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}")
        print(f"💪 Total Reps: {total_reps}")
        print(f"🏋️ Workout Sessions: {total_sessions}")
        print(f"⭐ Average Form Score: {avg_form_score:.1f}%")
        print(f"🔥 Calories Burned: {total_calories:.1f}")
        print(f"⏰ Total Time: {total_duration:.1f} minutes")
        print(f"🎪 Exercises: {', '.join(exercises_this_week)}")
        
        # Daily breakdown
        print("\n📅 DAILY BREAKDOWN:")
        daily_summary = week_data.groupby(week_data['date'].dt.date).agg({
            'total_reps': 'sum',
            'avg_form_score': 'mean',
            'duration_minutes': 'sum'
        }).round(1)
        
        for date, row in daily_summary.iterrows():
            print(f"  {date}: {row['total_reps']} reps, "
                  f"{row['avg_form_score']:.1f}% form, "
                  f"{row['duration_minutes']:.1f} min")
    
    def create_progress_charts(self):
        """Create visual progress charts"""
        sessions = self.data.get('session_history', [])
        if len(sessions) < 2:
            print("📊 Need at least 2 sessions for trend analysis")
            return
        
        df = pd.DataFrame(sessions)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Exercise Progress Analysis', fontsize=16)
        
        # 1. Reps over time
        axes[0, 0].plot(df['date'], df['total_reps'], marker='o', linewidth=2)
        axes[0, 0].set_title('Reps per Session')
        axes[0, 0].set_ylabel('Total Reps')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Form score over time
        axes[0, 1].plot(df['date'], df['avg_form_score'], 
                       marker='s', color='green', linewidth=2)
        axes[0, 1].set_title('Form Score Progress')
        axes[0, 1].set_ylabel('Average Form Score (%)')
        axes[0, 1].set_ylim(0, 100)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Exercise distribution
        exercise_counts = df['exercise_type'].value_counts()
        axes[1, 0].pie(exercise_counts.values, labels=exercise_counts.index, 
                      autopct='%1.1f%%', startangle=90)
        axes[1, 0].set_title('Exercise Distribution')
        
        # 4. Weekly volume
        df['week'] = df['date'].dt.isocalendar().week
        weekly_reps = df.groupby('week')['total_reps'].sum()
        axes[1, 1].bar(weekly_reps.index, weekly_reps.values, 
                      color='orange', alpha=0.7)
        axes[1, 1].set_title('Weekly Volume')
        axes[1, 1].set_ylabel('Total Reps')
        axes[1, 1].set_xlabel('Week Number')
        
        plt.tight_layout()
        
        # Save chart
        chart_filename = f"progress_chart_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Progress charts saved as {chart_filename}")
        
        # Show chart
        plt.show()
    
    def analyze_form_trends(self):
        """Analyze form score trends by exercise"""
        sessions = self.data.get('session_history', [])
        if not sessions:
            return
        
        df = pd.DataFrame(sessions)
        
        print("\n🎯 FORM ANALYSIS BY EXERCISE:")
        print("="*40)
        
        for exercise in df['exercise_type'].unique():
            exercise_data = df[df['exercise_type'] == exercise]
            
            avg_form = exercise_data['avg_form_score'].mean()
            best_form = exercise_data['avg_form_score'].max()
            worst_form = exercise_data['avg_form_score'].min()
            improvement = exercise_data['avg_form_score'].iloc[-1] - exercise_data['avg_form_score'].iloc[0] if len(exercise_data) > 1 else 0
            
            print(f"\n{exercise}:")
            print(f"  Average Form: {avg_form:.1f}%")
            print(f"  Best Session: {best_form:.1f}%")
            print(f"  Worst Session: {worst_form:.1f}%")
            print(f"  Improvement: {improvement:+.1f}%")
    
    def get_insights_and_recommendations(self):
        """Generate AI-powered insights and recommendations"""
        sessions = self.data.get('session_history', [])
        if not sessions:
            return
        
        df = pd.DataFrame(sessions)
        
        insights = []
        recommendations = []
        
        # Analyze consistency
        total_sessions = len(df)
        if total_sessions >= 5:
            recent_sessions = df.tail(5)
            form_variance = recent_sessions['avg_form_score'].std()
            
            if form_variance < 5:
                insights.append("✅ Your form consistency is excellent!")
            elif form_variance > 15:
                insights.append("⚠️  Your form varies significantly between sessions")
                recommendations.append("Focus on maintaining consistent technique")
        
        # Analyze progress
        if total_sessions >= 3:
            early_avg = df.head(3)['avg_form_score'].mean()
            recent_avg = df.tail(3)['avg_form_score'].mean()
            
            if recent_avg > early_avg + 5:
                insights.append("📈 Great progress! Your form is improving")
            elif recent_avg < early_avg - 5:
                insights.append("📉 Form scores have declined recently")
                recommendations.append("Consider reducing speed and focusing on technique")
        
        # Analyze volume
        avg_reps = df['total_reps'].mean()
        if avg_reps < 20:
            recommendations.append("Try increasing your rep count gradually for better endurance")
        elif avg_reps > 100:
            insights.append("🔥 Impressive volume! You're building great endurance")
        
        # Exercise variety
        unique_exercises = df['exercise_type'].nunique()
        if unique_exercises == 1:
            recommendations.append("Add variety by trying different exercises")
        elif unique_exercises >= 3:
            insights.append("🎪 Great exercise variety! This promotes balanced fitness")
        
        print("\n🤖 AI INSIGHTS:")
        print("="*30)
        for insight in insights:
            print(f"  {insight}")
        
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            print("="*30)
            for rec in recommendations:
                print(f"  • {rec}")
    
    def export_detailed_report(self):
        """Export detailed CSV report"""
        sessions = self.data.get('session_history', [])
        if not sessions:
            print("No data to export")
            return
        
        df = pd.DataFrame(sessions)
        filename = f"exercise_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"📄 Detailed report exported as {filename}")

# Example usage
if __name__ == "__main__":
    analytics = ExerciseAnalytics()
    analytics.generate_weekly_report()
    analytics.analyze_form_trends()
    analytics.get_insights_and_recommendations()