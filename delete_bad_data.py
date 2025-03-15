import os
import subprocess
import shutil

# define the base directory and python executable path
base_dir = "curated_data"  # modify the path to your A folder
python_executable = "python"
script_path = "3d_utlis/check_bad_data.py"

# iterate over all room_x subfolders in data folder
for room_folder in sorted(os.listdir(base_dir)):
    room_path = os.path.join(base_dir, room_folder)

    # only process room_x subfolders
    if not os.path.isdir(room_path) or not room_folder.startswith("room_"):
        continue

    print(f"Processing {room_folder}...")

    # build the command
    command = [
        python_executable,
        script_path,
        "--room_name", room_folder,
        "--step_number", "1",
        "--ground_truth", "true"
    ]

    # execute the command
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Success: {room_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error in {room_folder}: {e.stderr}")
        # delete the folder
        input("Press Enter to continue...")
        shutil.rmtree(room_path)
        print(f"Deleted {room_folder} due to error.")
