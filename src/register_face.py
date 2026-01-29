import cv2
import face_recognition
import pickle
import os

# =====================================================
# ABSOLUTE PROJECT PATH (NO RELATIVE PATH ISSUES)
# =====================================================

# Path to project root (face_attendence_system)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# encodings directory path
ENCODINGS_DIR = os.path.join(PROJECT_ROOT, "encodings")

# encoding file path
ENCODINGS_PATH = os.path.join(ENCODINGS_DIR, "face_encodings.pkl")

# Create encodings directory if it does not exist
os.makedirs(ENCODINGS_DIR, exist_ok=True)

print("PROJECT_ROOT:", PROJECT_ROOT)
print("ENCODINGS_DIR:", ENCODINGS_DIR)
print("ENCODINGS_PATH:", ENCODINGS_PATH)

# =====================================================
# USER INPUT
# =====================================================

user_name = input("Enter Name: ").strip()
user_id = input("Enter ID: ").strip()

# =====================================================
# LOAD EXISTING DATA (IF ANY)
# =====================================================

if os.path.exists(ENCODINGS_PATH):
    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)
else:
    data = {}

# =====================================================
# FACE CAPTURE
# =====================================================

cap = cv2.VideoCapture(0)
encodings = []
count = 0

print("📸 Look at the camera... Capturing face samples")

while count < 20:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)

    # Capture only when exactly ONE face is detected
    if len(boxes) == 1:
        encoding = face_recognition.face_encodings(rgb, boxes)[0]
        encodings.append(encoding)
        count += 1
        print(f"Captured {count}/20")

    cv2.imshow("Register Face", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# =====================================================
# SAVE ENCODINGS
# =====================================================

data[user_id] = {
    "name": user_name,
    "encodings": encodings
}

with open(ENCODINGS_PATH, "wb") as f:
    pickle.dump(data, f)

print("✅ Face registration completed successfully!")
print("📁 File created:", ENCODINGS_PATH)
