import cv2
import face_recognition
import pickle
import numpy as np
import os

from attendance import mark_attendance

# PATH SETUP
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCODINGS_PATH = os.path.join(PROJECT_ROOT, "encodings", "face_encodings.pkl")


# LOAD ENCODINGS
with open(ENCODINGS_PATH, "rb") as f:
    data = pickle.load(f)

known_encodings = []
known_names = []

for user in data.values():
    for enc in user["encodings"]:
        known_encodings.append(enc)
        known_names.append(user["name"])


# STATE TRACKING
# name -> state: NOT_SEEN | PUNCHED_IN | LEFT | PUNCHED_OUT
state = {}

# Track last action to avoid duplicate marks
last_action = {}

# CAMERA
cap = cv2.VideoCapture(0)
print("🎥 Attendance system started (press q to quit)")
print("📋 Instructions:")
print("   - Face detected first time → PUNCH IN")
print("   - Leave frame and return → PUNCH OUT")
print("   - After PUNCH OUT → Attendance complete for today")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    detected_names = set()

    for box, face_enc in zip(boxes, encodings):
        distances = face_recognition.face_distance(known_encodings, face_enc)
        index = np.argmin(distances)

        if distances[index] < 0.6:
            name = known_names[index]
            detected_names.add(name)

            # STATE MACHINE LOGIC
            # FIRST TIME SEEN → PUNCH IN
            if name not in state:
                status = mark_attendance(name)
                state[name] = "PUNCHED_IN"
                last_action[name] = status
                print(f"✅ {name}: {status}")
            
            # RETURNING AFTER LEAVING → PUNCH OUT
            elif state[name] == "LEFT":
                status = mark_attendance(name)
                state[name] = "PUNCHED_OUT"
                last_action[name] = status
                print(f"✅ {name}: {status}")
            
            # ALREADY PUNCHED IN (still in frame)
            elif state[name] == "PUNCHED_IN":
                status = "IN FRAME"
            
            # ALREADY PUNCHED OUT (attendance complete)
            elif state[name] == "PUNCHED_OUT":
                status = "ATTENDANCE COMPLETE"
            
            # Default fallback
            else:
                status = last_action.get(name, "UNKNOWN")

            # DISPLAY
            label = f"{name} - {status}"
            
            # Color coding
            if status == "PUNCH IN":
                color = (0, 255, 0)  # Green
            elif status == "PUNCH OUT":
                color = (0, 0, 255)  # Red
            elif status == "IN FRAME":
                color = (255, 165, 0)  # Orange
            elif status == "ATTENDANCE COMPLETE":
                color = (128, 128, 128)  # Gray
            else:
                color = (255, 255, 255)  # White

            top, right, bottom, left = box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, label, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

    # DETECT WHO LEFT THE FRAME    
    for name in list(state.keys()):
        # Only mark as LEFT if they were PUNCHED_IN and now not detected
        if state[name] == "PUNCHED_IN" and name not in detected_names:
            state[name] = "LEFT"
            print(f"👋 {name} left the frame (waiting for return to PUNCH OUT)")

    # Display frame
    cv2.imshow("Face Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
