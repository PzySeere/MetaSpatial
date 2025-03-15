import os
import json
import subprocess

A_folder = "curated_data"

room_folders = sorted([f for f in os.listdir(A_folder) if f.startswith("room_")])

failed_rooms = []

for room_name in room_folders:
    command = [
        "python",
        "./3d_utlis/check_bad_data.py",
        "--room_name", room_name,
        "--step_number", "1",
        "--ground_truth", "true"
    ]

    print(f"Processing: {room_name} ...")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"{room_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in {room_name}: {e}")
        failed_rooms.append(room_name)

# save failed rooms to json file
failed_rooms_path = os.path.join(A_folder, "failed_rooms.json")
with open(failed_rooms_path, "w") as f:
    json.dump(failed_rooms, f, indent=4)

print(f"Processing complete. Failed rooms saved to {failed_rooms_path}")
