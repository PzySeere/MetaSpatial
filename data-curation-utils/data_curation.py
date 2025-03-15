import json
import os
import multiprocessing
import argparse
from IDesign import IDesign
import psutil
import os

def cleanup_processes():
    """ forcefully terminate all child processes of the current Python process """
    current_process = psutil.Process(os.getpid())  # get the current Python process
    for child in current_process.children(recursive=True):  # get all child processes
        print(f"Terminating process {child.pid} ({child.name()})")  # print process information
        child.terminate()  # terminate the child process
    _, alive = psutil.wait_procs(current_process.children(recursive=True), timeout=5)
    for proc in alive:  # forcefully kill the remaining processes
        print(f"Killing process {proc.pid} ({proc.name()})")
        proc.kill()

# clean up before running
cleanup_processes()


parser = argparse.ArgumentParser(description="Process room design data in a given range.")
parser.add_argument("--start", type=int, required=True, help="Starting index of rooms to process")
parser.add_argument("--end", type=int, required=True, help="Ending index of rooms to process")
args = parser.parse_args()


json_path = "../generated_room_descriptions.json"
curated_data_path = "../curated_data"
with open(json_path, 'r') as f:
    room = json.load(f)

num_rooms = len(room)
start, end = args.start, args.end


if start < 0 or end > num_rooms or start >= end:
    print(f"Invalid range: start={start}, end={end}, total rooms={num_rooms}")
    exit(1)

print(f"Processing rooms from {start} to {end} out of {num_rooms}")


def process_room(i, timeout=1):
    os.makedirs(f"{curated_data_path}/room_{i}", exist_ok=True)
    initial_file = f"{curated_data_path}/room_{i}/scene_graph-initial.json"
    corrected_file = f"{curated_data_path}/room_{i}/scene_graph-corrected.json"
    refined_file = f"{curated_data_path}/room_{i}/scene_graph-refined.json"
    clustered_file = f"{curated_data_path}/room_{i}/scene_graph-clustered.json"
    backtracked_file = f"{curated_data_path}/room_{i}/scene_graph-backtracked.json"

    def process_logic():
        try:
            print(f"Starting IDesign for room {i}")  # add debug information
            input('dasdasdasd')
            i_design = IDesign(no_of_objects=10, user_input=str(room[i]['description']),
                               room_dimensions=[room[i]['size']['x'], room[i]['size']['y'], room[i]['size']['z']])
            i_design.create_initial_design()
            i_design.to_json(initial_file)
            i_design.correct_design()
            i_design.to_json(corrected_file)
            i_design.refine_design()
            i_design.to_json(refined_file)
            i_design.create_object_clusters(verbose=False)
            i_design.to_json(clustered_file)
            i_design.backtrack(verbose=True)
            i_design.to_json(backtracked_file)
        except Exception as e:
            print(f"Error processing room {i}: {e}")

    process = multiprocessing.Process(target=process_logic)
    process.start()
    process.join(timeout)  

    if process.is_alive():
        print(f"Room {i} exceeded {timeout} seconds, terminating...")
        process.terminate()  
        process.join()  

        for file in [initial_file, corrected_file, refined_file, clustered_file, backtracked_file]:
            if os.path.exists(file):
                os.remove(file)
        return False
    return True

for i in range(start, end):
    success = process_room(i, timeout=300)
    
    if success:
        print('--------------------------------')
        print(f'Completed {((i - start + 1) / (end - start)) * 100:.2f}% of assigned rooms')
        print('--------------------------------')
