import numpy as np
from copy import copy
import json

from metaverse_constraint_functions import get_above_constraint, get_behind_constraint, get_in_corner_constraint, get_in_front_constraint, get_left_of_constraint, get_right_of_constraint, get_on_constraint, get_under_contraint
def get_rotation(obj_A, scene_graph):
    # Get the rotation of an object in the scene graph
    layout_rot = {
        "west_wall" : 270.0,
        "east_wall" : 90.0,
        "north_wall" : 0.0,
        "south_wall" : 180.0,
        "middle of the room" : 0.0,
        "ceiling" : 0.0
    }

    if "rotation" in obj_A.keys():
        rot = obj_A["rotation"]["z_angle"]
    elif "facing" in obj_A.keys() and obj_A["facing"] in layout_rot.keys():
        rot = layout_rot[obj_A["facing"]]
    elif obj_A["new_object_id"] in layout_rot.keys():
        rot = layout_rot[obj_A["new_object_id"]]
    else: 
        parents = []
        for x in obj_A["placement"]["objects_in_room"]:
            try:
                p = [element for element in scene_graph if element.get("new_object_id") == x["object_id"]][0]
            except:
                print(f"Object {x['object_id']} not found in scene graph!")
                raise ValueError("Object not found in scene graph!")
            parents.append(p)
        if len(parents) > 0:
            parent = parents[0]
            rot = get_rotation(parent, scene_graph)
        else:
            rot = 0.0
    return rot
def is_thin_object(obj):
    """
    Returns True if the object is thin
    """
    size = obj["size_in_meters"]
    return min(size.values()) > 0.0 and max(size.values()) / min(size.values()) >= 40.0


def get_object_from_scene_graph(obj_id, scene_graph):
    """
    Get the object from the scene graph by its id
    """
    return next((x for x in scene_graph if x["new_object_id"] == obj_id), None)


def calculate_overlap(box1, box2):
    if box1 is None or box2 is None:
        return None
    
    x_min = max(box1[0], box2[0])
    x_max = min(box1[1], box2[1])
    y_min = max(box1[2], box2[2])
    y_max = min(box1[3], box2[3])
    z_min = max(box1[4], box2[4])
    z_max = min(box1[5], box2[5])
    
    # Check if the boxes overlap with a small tolerance
    if x_min <= x_max + 1e-03 and y_min <= y_max + 1e-03 and z_min <= z_max + 1e-03:
        return (x_min, x_max, y_min, y_max, z_min, z_max)
    else:
        return None

def is_collision_3d(obj1, obj2, bbox_instead = False):
    pos1, rot1, size1 = copy(obj1['position']), copy(obj1["rotation"]["z_angle"]), copy(obj1['size_in_meters'])
    # We won't check for collisions for objects with very thin surfaces
    if is_thin_object(obj1):
        return False
    if not bbox_instead:
        pos2, rot2, size2 = copy(obj2['position']), copy(obj2["rotation"]["z_angle"]), copy(obj2['size_in_meters'])
        # We won't check for collisions for objects with very thin surfaces
        try:
            if is_thin_object(obj2):
                return False
        except:
            print(obj2)
            raise Exception
    else:
        pos2, rot2, size2 = {"x" : (obj2[1] + obj2[0]) / 2 , "y" : (obj2[3] + obj2[2]) / 2, "z" : (obj2[5] + obj2[4]) / 2}, 0.0, {"length" : (obj2[1] - obj2[0]), "width" : (obj2[3] - obj2[2]), "height" : (obj2[5] - obj2[4])}


    def swap_dimensions_if_rotated(size, rotation):
        if np.isclose(rotation, 90.0) or np.isclose(rotation, 270.0):
            size["length"], size["width"] = size["width"], size["length"]

    def get_bounds(pos, size):
        x_max = pos['x'] + size['length'] / 2
        x_min = pos['x'] - size['length'] / 2
        y_max = pos['y'] + size['width'] / 2
        y_min = pos['y'] - size['width'] / 2
        z_max = pos['z'] + size['height'] / 2
        z_min = pos['z'] - size['height'] / 2
        return x_max, x_min, y_max, y_min, z_max, z_min

    def check_overlap(min1, max1, min2, max2):
        return min1 < max2 and max1 > min2 and abs(min1 - max2) > 1e-3 and abs(max1 - min2) > 1e-3

    # Swap dimensions if needed
    swap_dimensions_if_rotated(size1, rot1)
    swap_dimensions_if_rotated(size2, rot2)

    # Get bounds for both objects
    obj1_bounds = get_bounds(pos1, size1)
    obj2_bounds = get_bounds(pos2, size2)

    # Unpack bounds
    (obj1_x_max, obj1_x_min, obj1_y_max, obj1_y_min, obj1_z_max, obj1_z_min) = obj1_bounds
    (obj2_x_max, obj2_x_min, obj2_y_max, obj2_y_min, obj2_z_max, obj2_z_min) = obj2_bounds

    # Check for overlap in each dimension
    x_check = check_overlap(obj1_x_min, obj1_x_max, obj2_x_min, obj2_x_max)
    y_check = check_overlap(obj1_y_min, obj1_y_max, obj2_y_min, obj2_y_max)
    z_check = check_overlap(obj1_z_min, obj1_z_max, obj2_z_min, obj2_z_max)

    return x_check and y_check and z_check


def get_possible_positions(object_id, scene_graph, room_dimensions):
    obj = [element for element in scene_graph if element.get("new_object_id") == object_id][0]
    obj_scene_graph = obj["placement"]
    rot = get_rotation(obj, scene_graph)
    obj["rotation"] = {"z_angle" : rot}

    func_map = {
        "on" : get_on_constraint,
        "under" : get_under_contraint,
        "left of" : get_left_of_constraint,
        "right of" : get_right_of_constraint,
        "in front" : get_in_front_constraint,
        "behind" : get_behind_constraint,
        "above" : get_above_constraint,
        "in the corner" : get_in_corner_constraint,
        "in the middle of" : get_on_constraint
    }

    constraints = obj_scene_graph["room_layout_elements"] + obj_scene_graph["objects_in_room"]
    possible_positions = []
    for constraint in constraints:
        prep = constraint["preposition"]
        adjacency = constraint["is_adjacent"] if "is_adjacent" in constraint.keys() else True
        is_on_floor = obj["is_on_the_floor"]
        obj_A = obj
        key = "layout_element_id" if "layout_element_id" in constraint.keys() else "object_id"
        obj_B = [element for element in scene_graph if element.get("new_object_id") == constraint[key]][0]
        if "position" in obj_B.keys():
            possible_positions.append(func_map[prep](obj_A, obj_B, adjacency, is_on_floor, room_dimensions))

    return possible_positions



def check_collisions(scene_graph):
    """
    Check for 3D object collisions in the given scene graph.

    Args:
        scene_graph (list): JSON scene data containing all objects.

    Returns:
        collision_list (list): A list of object pairs that are colliding.
    """
    collision_list = []

    # Iterate through all objects in the scene
    for i, obj1 in enumerate(scene_graph):
        for j, obj2 in enumerate(scene_graph):
            if i >= j:
                continue  # Avoid redundant checks (A vs B is the same as B vs A)

            # Ensure both objects have a valid "position" key
            if "position" not in obj1 or "position" not in obj2:
                continue

            # Check for collision between obj1 and obj2
            if is_collision_3d(obj1, obj2):
                collision_list.append((obj1["new_object_id"], obj2["new_object_id"]))

    # Compute statistics
    total_objects = len(scene_graph)
    collision_count = len(collision_list)
    collision_ratio = collision_count / (total_objects * (total_objects - 1) / 2) if total_objects > 1 else 0

    # Print results
    print(f"✅ Total objects pairs: {total_objects * (total_objects - 1) / 2}")
    print(f"❌ Number of colliding object pairs: {collision_count}")
    print(f"📊 Collision ratio: {collision_ratio:.2%}")
    # Print the list of colliding objects
    # if collision_list:
    #     print("\n🚨 The following objects are colliding:")
    #     for obj1, obj2 in collision_list:
    #         print(f"- {obj1} ⛔ {obj2}")
    return collision_ratio

import json

def check_constraints(scene_graph, room_dimensions):
    """
    Check if all objects in the scene graph satisfy their spatial constraints.

    Args:
        scene_graph (list): JSON scene data containing all objects.
        room_dimensions (tuple): (room_length, room_width, room_height)

    Returns:
        violating_objects (list): A list of objects that do not satisfy constraints.
    """
    violating_objects = []

    # Iterate over all objects in the scene
    for obj in scene_graph[:-6]:
        if "position" not in obj:
            continue  # Skip objects without a defined position

        object_id = obj["new_object_id"]
        possible_positions = get_possible_positions(object_id, scene_graph, room_dimensions)

        # If no valid placement exists, mark as violating
        if not possible_positions:
            violating_objects.append(object_id)
            continue

        # Extract the object's current position
        x, y, z = obj["position"]["x"], obj["position"]["y"], obj["position"]["z"]
        
        # Check if the object falls within any valid placement constraints
        is_valid = False
        for pos in possible_positions:
            x_min, x_max, y_min, y_max, z_min, z_max = pos
            if x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max:
                is_valid = True
                break  # If it fits within one valid range, it's acceptable

        if not is_valid:
            violating_objects.append(object_id)

    # Compute statistics
    total_objects = len(scene_graph) - 6
    violating_count = len(violating_objects)
    violation_ratio = violating_count / total_objects if total_objects > 0 else 0

    # Print results
    print(f"✅ Total objects: {total_objects}")
    print(f"❌ Number of constraint violations: {violating_count}")
    print(f"📊 Violation ratio: {violation_ratio:.2%}")

    # List the objects that violate constraints
    if violating_objects:
        print("\n🚨 The following objects do not satisfy constraints:")
        for obj in violating_objects:
            print(f"- {obj}")
    return violation_ratio


