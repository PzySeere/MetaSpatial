# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import requests
import base64
import numpy as np
import re
import ast
from openai import OpenAI
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from metaverse_utils import check_constraints, check_collisions
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
rooms_folder = '/projects/p32364/MetaSpatial/curated_data'
# Example JSON format for the response
example_json = """
{
  "realism_and_3d_geometric_consistency": {
    "grade": 8,
    "comment": "The renders appear to have appropriate 3D geometry and lighting that is fairly consistent with real-world expectations. The proportions and perspective look realistic."
  },
  "functionality_and_activity_based_alignment": {
    "grade": 7,
    "comment": "The room includes a workspace, sleeping area, and living area as per the user preference. The L-shaped couch facing the bed partially meets the requirement for watching TV comfortably. However, there does not appear to be a TV depicted in the render, so it's not entirely clear if the functionality for TV watching is fully supported."
  },
  "layout_and_furniture": {
    "grade": 7,
    "comment": "The room has a bed that's not centered and with space at the foot, and a large desk with a chair. However, it's unclear if the height of the bed meets the user's preference, and the layout does not clearly show the full-length mirror in relation to the wardrobe, so its placement in accordance to user preferences is uncertain."
  },
  "color_scheme_and_material_choices": {
    "grade": 9, adheres to a light color scheme with blue and white tones as preferred by the user, without a nautical feel. The bed and other furniture choices are aligned with the color scheme specified."
  },
  "overall_aesthetic_and_atmosphere": {
    "grade": 8,
    "comment": "The room's general aesthetic is bright, clean, and relatively minimalistic, which could align with the user's preference for a light color scheme and a modern look. The chandelier is present as opposed to bright, hospital-like lighting."
  }
}
"""

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def gpt4o_evaluate_rooms(image_paths, user_preference, num_evaluations=1):
    """
    Evaluates room renders based on user preferences and returns scores.
    
    Args:
        image_paths: List of paths to room render images (typically 2)
        user_preference: User's text description of preferred room
        size_of_room: Size of the room
        num_evaluations: Number of times to run evaluation for averaging
    
    Returns:
        Dictionary containing evaluation scores with means and standard deviations
        The complete response from the final evaluation
    """
    # Prepare the evaluation prompt
    evaluation_prompt = f"""
    Give a grade from 1 to 10 or unknown to the following room renders based on how well they correspond together to the user preference (in triple backquotes) in the following aspects: 
    - Realism and 3D Geometric Consistency
    - Functionality and Activity-based Alignment
    - Layout and furniture  
    - Color Scheme and Material Choices
    - Overall Aesthetic and Atmosphere         
    User Preference:
    ```{user_preference}```
    Return the results in the following JSON format:
    ```json
    {example_json}
    ```
    """
    
    # Initialize grades dictionary for tracking scores
    grades = {
        "realism_and_3d_geometric_consistency": [],
        "functionality_and_activity_based_alignment": [],
        "layout_and_furniture": [],
        "color_scheme_and_material_choices": [],
        "overall_aesthetic_and_atmosphere": []
    }
    
    last_response = None
    
    # Run multiple evaluations to get a more reliable score
    for _ in range(num_evaluations):
        base64_image = image_to_base64(image_paths[0])
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": evaluation_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ]
        )
        response_text = completion.choices[0].message.content
        last_response = response_text
        print('response_text:', response_text)
        pattern = r'```json(.*?)```'
        matches = re.findall(pattern, response_text, re.DOTALL)
        json_content = matches[0].strip() if matches else None
        # print('--------------------------------')
        # print('json_content', json_content)
        # print('--------------------------------')
        # input('continue???')
        actual_string = ast.literal_eval(f"'''{json_content}'''")
        if json_content is None:
            try:
                grading = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Error parsing response: {response_text}")
                continue
        else:
            try:
                grading = json.loads(actual_string)
                # print('grading', grading)
                # input('continue???')
            except json.JSONDecodeError:
                print(f"Error parsing JSON content: {actual_string}")
                continue
                
        # Collect grades for each category
        for key in grades:
            if key in grading and "grade" in grading[key] and isinstance(grading[key]["grade"], (int, float)):
                grades[key].append(grading[key]["grade"])
    
    # Calculate mean and standard deviation for each category
    results = {}
    for key in grades:
        if grades[key]:  # Check if we have any valid grades
            results[key] = {
                "mean": round(sum(grades[key])/len(grades[key]), 2), 
                "std": round(np.std(grades[key]), 2)
            }
        else:
            results[key] = {"mean": 0, "std": 0}
    
    # Generate output filename based on first image path
    base_name = os.path.basename(image_paths[0])
    output_name = f"{os.path.splitext(base_name)[0]}_grades.json"
    
    # Save results to JSON file
    # with open(output_name, "w") as f:
    #     json.dump(results, f, indent=2)
    print('--------------------------------')
    print('results', results)
    print('--------------------------------')
    return results, last_response
def extract_json_from_text(text):
    pattern = r"<answer>\s*(.*?)\s*</answer>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1) 
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return None
    else:
        return None
    
def metaverse_format_reward(predict_str: str, room_name: str) -> float:
    pattern = re.compile(r"^\s*<think>.*?</think>\s*<answer>.*?</answer>\s*$", re.DOTALL)
    format_match = re.fullmatch(pattern, predict_str)
    if not format_match:
        return 0
    answer_json = extract_json_from_text(format_match.group(0))
    if answer_json is None:
        return 0.1
    final_json = json.loads(open(os.path.join(rooms_folder, room_name, 'scene_graph-backtracked.json')).read())[:-6]
    if len(answer_json) != len(final_json):
        print('length mismatch', len(answer_json), len(final_json))
        return 0.5
    return 1.0


def metaverse_gpt4_reward(predict_str: str, room_name: str, user_preference: str, size_of_room: str, step_number) -> float:
    answer_json = extract_json_from_text(predict_str)
    if answer_json is None:
        print("Error: answer_json is None!")
        print('--------------------------------')
        print('answer_json', answer_json)
        print('predict_str', predict_str)
        print('--------------------------------')
        # input('continue???')
        return 10

    if not isinstance(answer_json, list):
        print(f"Error: answer_json is not a list, got {type(answer_json)}: {answer_json}")
        print('--------------------------------')
        print('answer_json', answer_json)
        print('predict_str', predict_str)
        print('--------------------------------')
        answer_json = [answer_json]
        # input('continue???')
        # return 0.1

    if len(answer_json) == 0:
        print("Error: answer_json is an empty list!")
        print('--------------------------------')
        print('answer_json', answer_json)
        print('predict_str', predict_str)
        print('--------------------------------')
        # input('continue???')
        return 10
    try:
        final_json = json.loads(open(os.path.join(rooms_folder, room_name, 'scene_graph-backtracked.json')).read())
        # print(answer_json[0])
        # print('--------------------------------')
        # print('original final_json', final_json[0])
        # print('--------------------------------')
        dict = {obj['new_object_id']: obj for obj in final_json[:-6]}
        if len(answer_json) != len(final_json[:-6]):
            print('length mismatch', len(answer_json), len(final_json[:-6]))
            return 10
        # try catch to avoid error when object id is not in the dict

        for obj in answer_json:
            obj_id = obj['new_object_id']
            if obj_id not in dict:
                return 0
            final_obj = dict[obj_id]
            final_obj['position']['x'] = obj['x']
            final_obj['position']['y'] = obj['y']
            final_obj['position']['z'] = obj['z']
        print('updated final_json', final_json[0])
        print('--------------------------------')
        #save updated final_json
        with open(os.path.join(rooms_folder, room_name, 'scene_graph-backtracked-updated.json'), 'w') as f:
            json.dump(final_json, f, indent=4)
        print(f"File written successfully: {os.path.join(rooms_folder, room_name, 'scene_graph-backtracked-updated.json')}")
        #generate the blend file and render the image
        os.system(f'/projects/p32364/envs/3d-retriever/bin/python /projects/p32364/MetaSpatial/3d_utlis/place_in_blender.py --room_name {room_name} --step_number {step_number} --ground_truth false')
        image_path = os.path.join(rooms_folder, room_name, f'render_output_step_{step_number}.png')
        #evaluate the image
        grading, last_response = gpt4o_evaluate_rooms([image_path], user_preference)
        print('--------------------------------')
        print('grading', grading)
        print('--------------------------------')
        print('last_response', last_response)
        print('--------------------------------')
    except Exception as e:
        print('Exception', e)
        return 0    
    return grading

def metaverse_compute_score(predict_str: str, ground_truth: str, step_number: int) -> float:
    ground_truth_json = json.loads(ground_truth)
    print('ground_truth_json', ground_truth_json)
    room_name = ground_truth_json['room_name']
    user_preference = ground_truth_json['user_preference']
    size_of_room = ground_truth_json['size_of_room']    
    format_reward = metaverse_format_reward(predict_str, room_name)
    print('format_reward', format_reward)
    if format_reward == 1.0:
        print('format_reward', format_reward)
        gpt4_reward = metaverse_gpt4_reward(predict_str, room_name, user_preference, size_of_room, step_number)
    else:
        return 0.5*format_reward
    print('gpt4_reward', gpt4_reward)
    if isinstance(gpt4_reward, dict):
        gpt4_final_reward = int(gpt4_reward['overall_aesthetic_and_atmosphere']['mean']) + int(gpt4_reward['color_scheme_and_material_choices']['mean']) + int(gpt4_reward['layout_and_furniture']['mean']) + int(gpt4_reward['functionality_and_activity_based_alignment']['mean']) + int(gpt4_reward['realism_and_3d_geometric_consistency']['mean'])
    else:
        gpt4_final_reward = gpt4_reward
    if gpt4_final_reward == 0:
        return 0.5*format_reward
    if gpt4_final_reward == 10:
        return 0.5*format_reward + gpt4_final_reward / 50
    
    file_name = os.path.join(rooms_folder, room_name, 'scene_graph-backtracked-updated.json')
    scene_graph = json.loads(open(file_name).read())
    collision_ratio = check_collisions(scene_graph) 
    constraint_ratio = check_constraints(scene_graph, room_dimensions=(size_of_room['x'], size_of_room['y'], size_of_room['z']))
    print('gpt4_final_reward', gpt4_final_reward)
    print('collision_ratio', collision_ratio)
    print('constraint_ratio', constraint_ratio)
    return gpt4_final_reward / 50 + 0.5*format_reward - 0.2*collision_ratio - 0.2*constraint_ratio

# string = '<think>\nThe goal is to arrange the objects in a kitchen setting that includes a large island, hanging pots and pans, bar stools, a refrigerator, an oven, a pantry cabinet, a range hood, a dining table, and respect the spatial constraints and user preferences. Here\'s how we can approach this:\n\n1. **Kitchen Island**: Place it centrally in the room, as it is the focal point of the kitchen.\n2. **Hanging Pot Rack**: Hang it above the kitchen island.\n3. **Bar Stools**: Place them around the kitchen island, ensuring they are not too close to the island or each other.\n4. **Refrigerator**: Place it against the south wall, slightly left of the middle of the room.\n5. **Oven**: Place it next to the refrigerator, right of it.\n6. **Pantry Cabinet**: Place it against the south wall, slightly right of the refrigerator.\n7. **Range Hood**: Hang it above the oven.\n8. **Dining Table**: Place it in the corner formed by the north and west walls.\n\nLet\'s compute the positions:\n\n- **Kitchen Island**: Centralized at (3, 2.5, 0.45)\n- **Hanging Pot Rack**: Above the kitchen island at (3, 2.5, 0.65)\n- **Bar Stools**:\n  - Bar Stool 1: Right of the kitchen island at (3.5, 2.5, 0.45)\n  - Bar Stool 2: Left of the kitchen island at (2.5, 2.5, 0.45)\n  - Bar Stool 3: In front of the kitchen island at (3, 3.5, 0.45)\n  - Bar Stool 4: Behind the kitchen island at (3, 1.5, 0.45)\n- **Refrigerator**: Against the south wall at (3, 0, 0.45)\n- **Oven**: Next to the refrigerator at (3, 0, 0.45)\n- **Pantry Cabinet**: Against the south wall at (4, 0, 0.45)\n- **Range Hood**: Above the oven at (3, 0, 0.65)\n- **Dining Table**: In the corner at (0, 2.5, 0.45)\n\nNow, let\'s generate the JSON output.\n</think>\n<answer>\n[\n    {"new_object_id": "kitchen_island_1", "x": 3.0, "y": 2.5, "z": 0.45},\n    {"new_object_id": "hanging_pot_rack_1", "x": 3.0, "y": 2.5, "z": 0.65},\n    {"new_object_id": "bar_stool_1", "x": 3.5, "y": 2.5, "z": 0.45},\n    {"new_object_id": "bar_stool_2", "x": 2.5, "y": 2.5, "z": 0.45},\n    {"new_object_id": "bar_stool_3", "x": 3.0, "y": 3.5, "z": 0.45},\n    {"new_object_id": "bar_stool_4", "x": 3.0, "y": 1.5, "z": 0.45},\n    {"new_object_id": "refrigerator_1", "x": 3.0, "y": 0, "z": 0.45},\n    {"new_object_id": "oven_1", "x": 3.0, "y": 0, "z": 0.45},\n    {"new_object_id": "pantry_cabinet_1", "x": 4.0, "y": 0, "z": 0.45},\n    {"new_object_id": "ceiling_mounted_range_hood_1", "x": 3.0, "y": 0, "z": 0.65},\n    {"new_object_id": "dining_table_1", "x": 0, "y": 2.5, "z": 0.45}\n]\n</answer>'
# ground_truth = """{"room_name": "room_2106", "user_preference": "A bustling kitchen with a large island, hanging pots and pans, and a delicious aroma of freshly baked bread.", "size_of_room": {"x": 6, "y": 5, "z": 3}}"""

# # print('metaverse_compute_score', metaverse_compute_score(string, ground_truth))
# # user_preference = "A modern office space with sleek desks and ergonomic chairs, the soft hum of computers and the gentle tapping of keyboards fills the room."
# # print(gpt4o_evaluate_rooms(["/projects/p32364/Metaverse-R1/curated_data/room_4/render_output_step_1.png"], user_preference, num_evaluations=1))   

# # check_collisions(json.loads(open('/projects/p32364/Metaverse-R1/curated_data/room_2138/scene_graph-backtracked.json').read()))
# # check_constraints(json.loads(open('/projects/p32364/Metaverse-R1/curated_data/room_2138/scene_graph-backtracked.json').read()), room_dimensions=(4, 4, 2.5))

# metaverse_compute_score(string, ground_truth)