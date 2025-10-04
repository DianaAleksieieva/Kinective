# 📐 Camera Positioning Guide for Exercise Tracking

## 🎯 **Optimal Camera Angles for Each Exercise**

### **Bicep Curls - 90° Side View (Profile)**
```
📹 Camera Position: 90° to the side
🏃‍♂️ User Position: Standing sideways
📏 Distance: 3-4 feet from camera
💡 Lighting: Even lighting on side profile

    📹
    |
    |     🏃‍♂️ <- User (side view)
    |      |\
    |      | \🏋️
    |
```
**Why**: Clear elbow angle visibility, no arm occlusion

### **Push-ups - 45° Diagonal View**
```
📹 Camera Position: 45° diagonal above
🏃‍♂️ User Position: On floor, facing diagonal
📏 Distance: 4-5 feet from camera
💡 Lighting: Overhead lighting preferred

        📹
       /
      /
    🏃‍♂️ <- User (diagonal view)
```
**Why**: See both arms, body alignment, and elbow angles

### **Squats - Front View (0°)**
```
📹 Camera Position: Directly in front
🏃‍♂️ User Position: Facing camera
📏 Distance: 4-5 feet from camera
💡 Lighting: Even front lighting

📹 ← → 🏃‍♂️ (front view)
```
**Why**: Clear knee tracking, hip movement, and balance

## 🔧 **General Setup Tips**

### **📱 Camera Height**
- **Bicep Curls**: Elbow height (when arm is at 90°)
- **Push-ups**: Chest height (when in plank position)
- **Squats**: Hip height (standing position)

### **💡 Lighting Requirements**
- ✅ **Even lighting** - avoid harsh shadows
- ✅ **Bright enough** for clear keypoint detection
- ❌ **Avoid backlighting** (window behind you)
- ❌ **Avoid side shadows** from single light source

### **🎨 Background**
- ✅ **Plain, solid background** (wall, solid color)
- ✅ **Contrasting color** to your clothing
- ❌ **Busy patterns** or cluttered backgrounds
- ❌ **Similar colors** to your clothing

### **👕 Clothing**
- ✅ **Fitted clothing** for better pose detection
- ✅ **Contrasting colors** to background
- ✅ **Short sleeves** for arm exercises
- ❌ **Loose, baggy clothing**
- ❌ **Same color as background**

## 📊 **Detection Quality Indicators**

### **✅ Good Detection Signs:**
- Smooth angle measurements
- Consistent keypoint tracking
- No jittery movements in display
- Rep counting works accurately

### **❌ Poor Detection Signs:**
- Jumpy angle readings
- Missing keypoints (red dots)
- Inconsistent rep counting
- "No pose detected" messages

## 🛠️ **Troubleshooting Common Issues**

### **Problem: Jittery Angle Readings**
**Solutions:**
- Move farther from camera
- Improve lighting
- Wear more fitted clothing
- Check for background distractions

### **Problem: Missing Keypoints**
**Solutions:**
- Ensure full body/arm visibility
- Improve lighting conditions
- Move to optimal angle position
- Check camera focus

### **Problem: Inaccurate Rep Counting**
**Solutions:**
- Slow down movement speed
- Increase range of motion
- Check camera angle alignment
- Ensure complete reps (full ROM)

### **Problem: "No Pose Detected"**
**Solutions:**
- Step back from camera
- Improve room lighting
- Change background
- Check camera is working

## 📐 **Angle-Specific Optimization**

### **For Bicep Curls (Side View):**
```python
# Optimal angles we look for:
Extended (down): 160-170°    # Nearly straight arm
Contracted (up): 35-50°      # Full bicep contraction
```

### **For Push-ups (Diagonal View):**
```python
# Optimal angles we look for:
Up position: 160-170°        # Arms extended
Down position: 70-90°        # Good depth
```

### **Camera Distance by Exercise:**
- **Bicep Curls**: 3-4 feet (close, focused on upper body)
- **Push-ups**: 4-5 feet (full body view needed)
- **Squats**: 4-6 feet (full body + movement space)

## 🎯 **Quick Setup Checklist**

Before starting any exercise tracker:

- [ ] Camera at correct height for exercise
- [ ] Proper angle (side/front/diagonal)
- [ ] 3-5 feet distance from camera
- [ ] Good, even lighting
- [ ] Plain background
- [ ] Fitted, contrasting clothing
- [ ] Full movement range visible
- [ ] Test with a few practice reps

**Remember: 30 seconds of good setup = 30 minutes of accurate tracking!** 🚀