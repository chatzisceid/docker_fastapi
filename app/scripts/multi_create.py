import cv2
import os

# Set up video capture
video_path = '/path/to/your/video.mp4'
output_folder = '/path/to/output/folder'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Capture video frames
cap = cv2.VideoCapture(video_path)
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Save frame as JPEG
    cv2.imwrite(os.path.join(output_folder, f'frame_{frame_count:06d}.jpg'), frame)
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
