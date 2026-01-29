import os
import pandas as pd
from datetime import datetime

# =====================================================
# PATH SETUP
# =====================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# =====================================================
# MARK ATTENDANCE FUNCTION (FULLY FIXED)
# =====================================================

def mark_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Create CSV if not exists
    if not os.path.exists(ATTENDANCE_FILE):
        df = pd.DataFrame(
            columns=["Name", "Date", "Punch In", "Punch Out"]
        )
        df.to_csv(ATTENDANCE_FILE, index=False)
        print("📁 Created new attendance file")

    # Read CSV with proper NaN handling
    df = pd.read_csv(ATTENDANCE_FILE, keep_default_na=False)
    
    # Ensure all columns are strings (prevents NaN issues)
    df["Name"] = df["Name"].astype(str)
    df["Date"] = df["Date"].astype(str)
    df["Punch In"] = df["Punch In"].astype(str)
    df["Punch Out"] = df["Punch Out"].astype(str)

    # Get today's record for this user
    user_today = df[(df["Name"] == name) & (df["Date"] == today)]

    # -------------------------------
    # PUNCH IN (first appearance)
    # -------------------------------
    if user_today.empty:
        new_row = pd.DataFrame([{
            "Name": name,
            "Date": today,
            "Punch In": current_time,
            "Punch Out": ""
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        print(f"✅ PUNCH IN recorded: {name} at {current_time}")
        return "PUNCH IN"

    # -------------------------------
    # PUNCH OUT (return after leaving)
    # -------------------------------
    idx = user_today.index[0]
    punch_out_value = str(df.at[idx, "Punch Out"]).strip()
    
    print(f"🔍 Debug: Current Punch Out value: '{punch_out_value}' (type: {type(punch_out_value)})")

    # Check if punch out is empty (handle various empty representations)
    if punch_out_value == "" or punch_out_value == "nan" or pd.isna(punch_out_value):
        df.at[idx, "Punch Out"] = current_time
        
        # Save with explicit handling to prevent NaN conversion
        df.to_csv(ATTENDANCE_FILE, index=False, na_rep="")
        
        print(f"✅ PUNCH OUT recorded: {name} at {current_time}")
        print(f"📊 Updated row: {df.loc[idx].to_dict()}")
        
        return "PUNCH OUT"

    # -------------------------------
    # ALREADY MARKED (both times exist)
    # -------------------------------
    print(f"⚠️ Already marked: Punch In={df.at[idx, 'Punch In']}, Punch Out={punch_out_value}")
    return "ALREADY MARKED"