import json
import os
from PIL import Image
from datasets import Dataset, DatasetDict, Features, Image as HFImage, Value
import numpy as np

# 读取房间描述数据
room_description = json.load(open('../generated_room_descriptions.json'))
total_count = len(room_description)
success_count = 0
data = []

for i in range(len(room_description)):
    # if success_count >= 100:  # 只处理 100 个房间
    #     break
    user_input = str(room_description[i]['description'])
    size_of_room = str(room_description[i]['size'])

    try:
        room = json.load(open(f'/projects/p32364/MetaSpatial/curated_data/room_{i}/scene_graph-backtracked.json'))
        success_count += 1
    except:
        print(f'scene_graph-{i}-backtracked.json not found')
        continue
    if room is None:
        print(f"Warning: scene_graph-backtracked.json for room_{i} is empty or invalid")
        continue

    for obj in room[:-6]:
        if "position" in obj:
            del obj["position"]

    formatted_room = json.dumps(room, indent=2)
    
    # 处理图片
    room_image = Image.open(f"/projects/p32364/MetaSpatial/curated_data/room_{i}/render_output.png")
    room_image = room_image.resize((200, 200))
    room_image.save(f"/projects/p32364/MetaSpatial/curated_data/room_{i}/render_output_200.png")
    room_image = Image.open(f"/projects/p32364/MetaSpatial/curated_data/room_{i}/render_output_200.png")

    prompt = f"""<image>
    ## Task Description
    You are an intelligent assistant for arranging objects in a room based on JSON data. The given image is the shape of the room. Your task is to:
    1. Compute spatial coordinates for each object, respecting room layout and constraints.
    2. Ensure logical placement by preventing object collisions and respecting spatial boundaries.
    3. Respect user preferences when arranging objects.

    ## Room Information
    - Room Dimensions: {size_of_room} (Length meter × Width meter × Height meter).
    - Room Layout Elements (reference points for object placement):  
    ['south_wall', 'north_wall', 'west_wall', 'east_wall', 'middle of the room', 'ceiling'].

    ## User Preferences
    {user_input}
    ## Placement Rules:
    ### 1. Compute the Spatial Coordinates of Each Object and Generate a "positions" (x, y, z) field for each object.
    ### 2. Ensure Objects Do Not Collide
    ### 3. Maintain Logical Consistency

    ## Output Format
    First reason about the placement logic and provide a step-by-step explanation within the <think> </think> tags. After the reasoning process, the final output must be structured in JSON format within <answer> </answer> tags. Only output the generated position of the objects. Do not output the original object information like style, material, size_in_meters, etc.
    ---
    ## Expected Output
    <think>
    Thinking process here.
    </think>
    <answer>
    {{"new_object_id": "sectional_sofa_1","x": 1.0,"y": 1.8274559707043474,"z": 0.45}}, {{"new_object_id": "sectional_sofa_2","x": 1.0,"y": 1.8274559707043474,"z": 0.45}}}}
    </answer>
    ## Input JSON Data:
    """ + formatted_room

    answer = json.dumps({
        "room_name": f"room_{i}",
        "user_preference": user_input,
        "size_of_room": json.loads(size_of_room.replace("'", '"'))
    }, ensure_ascii=False)

    data.append({
        'images': [room_image],
        'problem': prompt,
        'answer': answer
    })

# split the dataset
length = len(data)
train_data = data[:int(length*0.8)]
test_data = data[int(length*0.8):]

# define the dataset features
features = Features({
    "images": [HFImage()], 
    "problem": Value("string"),
    "answer": Value("string")
})

# create the train and test dataset
dataset = DatasetDict({
    "train": Dataset.from_list(train_data, features=features),
    "test": Dataset.from_list(test_data, features=features)
})

# upload to Hugging Face Hub
dataset.push_to_hub("zhenyupan/3d_layout_reasoning_800")

# save to local
# dataset.save_to_disk("3d_layout_reasoning")
# dataset["train"].to_json("3d_layout_reasoning_train.json")
# dataset["test"].to_json("3d_layout_reasoning_test.json")
# dataset["train"].to_csv("3d_layout_reasoning_train.csv")
# dataset["test"].to_csv("3d_layout_reasoning_test.csv")
