from ultralytics import YOLO

# Load a pretrained YOLO model (recommended for training)
model = YOLO("yolo11n.pt")

print("Model loaded successfully!")
print(f"Model type: {type(model)}")

# Perform object detection on an image using the model
print("Running inference on a test image...")
results = model("https://ultralytics.com/images/bus.jpg")

print("Inference completed!")
print(f"Number of detections: {len(results)}")

# Process results
for r in results:
    print(f"Image shape: {r.orig_shape}")
    print(f"Number of detections in this image: {len(r.boxes)}")
    
    # Print detection details
    if r.boxes is not None:
        for i, box in enumerate(r.boxes):
            cls = int(box.cls.item())
            conf = float(box.conf.item())
            print(f"Detection {i+1}: Class={cls} Confidence={conf:.2f}")