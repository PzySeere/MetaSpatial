from copy import copy

def get_on_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is on obj_B
    """
    size_A = copy(obj_A["size_in_meters"])

    
    pos_B = obj_B["position"]
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]
    if obj_B["rotation"]["z_angle"] in [90.0, 270.0]:
        size_B["length"], size_B["width"] = size_B["width"], size_B["length"]

    if obj_B["new_object_id"] not in ["south_wall", "north_wall", "east_wall", "west_wall", "ceiling"]:
        z_min = pos_B["z"] + size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2 
        z_max = pos_B["z"] + size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2 
        x_min = pos_B["x"] - size_B["length"] / 2 + size_A["length"] / 2
        x_max = pos_B["x"] + size_B["length"] / 2 - size_A["length"] / 2
        y_min = pos_B["y"] - size_B["width"] / 2 + size_A["width"] / 2
        y_max = pos_B["y"] + size_B["width"] / 2 - size_A["width"] / 2
    elif obj_B["new_object_id"] == "ceiling":
        z_min = pos_B["z"] - size_B["height"] / 2 - size_A["height"] / 2
        z_max = pos_B["z"] - size_B["height"] / 2 - size_A["height"] / 2
        x_min = pos_B["x"] - size_B["length"] / 2 + size_A["length"] / 2
        x_max = pos_B["x"] + size_B["length"] / 2 - size_A["length"] / 2
        y_min = pos_B["y"] - size_B["width"] / 2 + size_A["width"] / 2
        y_max = pos_B["y"] + size_B["width"] / 2 - size_A["width"] / 2
    elif obj_B["new_object_id"] == "middle of the room":
        z_min = pos_B["z"] + size_B["height"] / 2 + size_A["height"] / 2
        z_max = pos_B["z"] + size_B["height"] / 2 + size_A["height"] / 2
        x_min = pos_B["x"] - size_B["length"] / 2 + size_A["length"] / 2
        x_max = pos_B["x"] + size_B["length"] / 2 - size_A["length"] / 2
        y_min = pos_B["y"] - size_B["width"] / 2 + size_A["width"] / 2
        y_max = pos_B["y"] + size_B["width"] / 2 - size_A["width"] / 2
    else:
        z_min = pos_B["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2 
        z_max = pos_B["z"] + size_B["height"] / 2 - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
        sign_map = {
            "west_wall" : (+1, +1, -1, +1, +1, +1, +1, -1),
            "east_wall" : (-1, -1, -1, +1, -1, -1, +1, -1),
            "north_wall" : (-1, +1, -1, -1, +1, -1, -1, -1),
            "south_wall" : (-1, +1, +1, +1, +1, -1, +1, +1),
        }  
        x_min = pos_B["x"] + sign_map[obj_B["new_object_id"]][0] * size_B["length"] / 2 + sign_map[obj_B["new_object_id"]][4] * size_A["length"] / 2 
        x_max = pos_B["x"] + sign_map[obj_B["new_object_id"]][1] * size_B["length"] / 2 + sign_map[obj_B["new_object_id"]][5] * size_A["length"] / 2
        y_min = pos_B["y"] + sign_map[obj_B["new_object_id"]][2] * size_B["width"] / 2 + sign_map[obj_B["new_object_id"]][6] * size_A["width"] / 2
        y_max = pos_B["y"] + sign_map[obj_B["new_object_id"]][3] * size_B["width"] / 2 + sign_map[obj_B["new_object_id"]][7] * size_A["width"] / 2

    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    if z_min > z_max:
        z_min, z_max = z_max, z_min

    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)
    z_max = max(size_A["height"] / 2, min(z_max, room_dimensions[2] - size_A["height"] / 2))
    z_min = max(z_min, 0.0 + size_A["height"] / 2)

    return (x_min, x_max, y_min, y_max, z_min, z_max)

def get_under_contraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is under obj_B
    """

    size_A = copy(obj_A["size_in_meters"])
    
    pos_B = obj_B["position"]
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]
    if obj_B["rotation"]["z_angle"] in [90.0, 270.0]:
        size_B["length"], size_B["width"] = size_B["width"], size_B["length"]

    z_min = size_A["height"] / 2
    z_max = pos_B["z"] - size_B["height"] / 2 - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    x_min = pos_B["x"] - size_B["length"] / 2 - size_A["length"] / 2
    x_max = pos_B["x"] + size_B["length"] / 2 + size_A["length"] / 2
    y_min = pos_B["y"] - size_B["width"] / 2 - size_A["width"] / 2
    y_max = pos_B["y"] + size_B["width"] / 2 + size_A["width"] / 2
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    if z_min > z_max:
        z_min, z_max = z_max, z_min
    
    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)
    z_max = max(size_A["height"] / 2, min(z_max, room_dimensions[2] - size_A["height"] / 2))
    z_min = max(z_min, 0.0 + size_A["height"] / 2)
    
    return (x_min, x_max, y_min, y_max, z_min, z_max)


def get_left_of_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is left of obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]


    z_min = obj_B["position"]["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    z_max = room_dimensions[2] - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2 if is_adjacent else size_A["length"] / 2
        x_max = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2 if is_adjacent else room_dimensions[1] - size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 180.0:
        x_min = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2 if is_adjacent else room_dimensions[0] - size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 if is_adjacent else size_A["width"] / 2
        y_max = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)

    
    return (x_min, x_max, y_min, y_max, z_min, z_max)           


def get_right_of_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is right of obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]

    z_min = obj_B["position"]["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    z_max = room_dimensions[2] - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_min = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2 if is_adjacent else room_dimensions[0] - size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 
        y_max = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 if is_adjacent else size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 180.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2 if is_adjacent else size_A["length"] / 2
        x_max = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2 
        y_min = obj_B["position"]["y"] + size_B["width"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] - size_B["width"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_min = obj_B["position"]["x"] + size_B["width"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] - size_B["width"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2 if is_adjacent else room_dimensions[1] - size_A["width"] / 2
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)
    
    return (x_min, x_max, y_min, y_max, z_min, z_max)

def get_in_front_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is in front of obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]


    z_min = obj_B["position"]["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    z_max = room_dimensions[2] - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 if is_adjacent else room_dimensions[1] - size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_min = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 if is_adjacent else room_dimensions[0] - size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 180.0 :
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2 if is_adjacent else size_A["width"] / 2
        y_max = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2 
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 if is_adjacent else size_A["length"] / 2
        x_max = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    
    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)
    
    return (x_min, x_max, y_min, y_max, z_min, z_max)
    
def get_behind_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is behind obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]


    z_min = obj_B["position"]["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    z_max = room_dimensions[2] - size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2 if is_adjacent else size_A["width"] / 2
        y_max = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2 
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 if is_adjacent else size_A["length"] / 2
        x_max = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    elif obj_B["rotation"]["z_angle"] == 180.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 + ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 - ((is_adjacent * size_A["length"]) - (not is_adjacent * size_A["length"])) / 2
        y_min = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 if is_adjacent else room_dimensions[1] - size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_min = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 if is_adjacent else room_dimensions[0] - size_A["length"] / 2
        y_min = obj_B["position"]["y"] + size_B["length"] / 2 - ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
        y_max = obj_B["position"]["y"] - size_B["length"] / 2 + ((is_adjacent * size_A["width"]) - (not is_adjacent * size_A["width"])) / 2
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)

    return (x_min, x_max, y_min, y_max, z_min, z_max)

def get_above_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is above obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]


    z_min = obj_B["position"]["z"] + size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2
    z_max = room_dimensions[2] if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 180.0:
        x_min = obj_B["position"]["x"] - size_B["length"] / 2 - size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["length"] / 2 + size_A["length"] / 2
        y_min = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2
        y_max = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_min = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        x_max = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        y_min = obj_B["position"]["y"] - size_B["length"] / 2 - size_A["width"] / 2 
        y_max = obj_B["position"]["y"] + size_B["length"] / 2 + size_A["width"] / 2
    
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    
    x_max = max(size_A["length"] / 2, min(x_max, room_dimensions[0] - size_A["length"] / 2))
    x_min = max(x_min, 0.0 + size_A["length"] / 2)
    y_max = max(size_A["width"] / 2, min(y_max, room_dimensions[1] - size_A["width"] / 2))
    y_min = max(y_min, 0.0 + size_A["width"] / 2)
    z_min = max(size_A["height"] / 2, min(z_min, room_dimensions[2] - size_A["height"] / 2))
    z_min = max(z_min, 0.0 + size_A["height"] / 2)

    return (x_min, x_max, y_min, y_max, z_min, z_max)


def get_in_corner_constraint(obj_A, obj_B, is_adjacent, is_on_floor, room_dimensions):
    """
    obj_A is in the corner of obj_B
    """
    size_A = copy(obj_A["size_in_meters"])
    size_B = copy(obj_B["size_in_meters"])

    if obj_A["rotation"]["z_angle"] in [90.0, 270.0]:
        size_A["length"], size_A["width"] = size_A["width"], size_A["length"]


    z_min = obj_B["position"]["z"] - size_B["height"] / 2 + size_A["height"] / 2 if not is_on_floor else size_A["height"] / 2

    if obj_B["rotation"]["z_angle"] == 0.0:
        x_1 = obj_B["position"]["x"] - size_B["length"] / 2 + size_A["length"] / 2 
        x_2 = obj_B["position"]["x"] + size_B["length"] / 2 - size_A["length"] / 2 
        y_1 = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 
        y_2 = obj_B["position"]["y"] + size_B["width"] / 2 + size_A["width"] / 2 
    elif obj_B["rotation"]["z_angle"] == 90.0:
        x_1 = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        x_2 = obj_B["position"]["x"] + size_B["width"] / 2 + size_A["length"] / 2 
        y_1 = obj_B["position"]["y"] - size_B["length"] / 2 + size_A["width"] / 2 
        y_2 = obj_B["position"]["y"] + size_B["length"] / 2 - size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 180.0:
        x_1 = obj_B["position"]["x"] - size_B["length"] / 2 + size_A["length"] / 2 
        x_2 = obj_B["position"]["x"] + size_B["length"] / 2 - size_A["length"] / 2 
        y_1 = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2 
        y_2 = obj_B["position"]["y"] - size_B["width"] / 2 - size_A["width"] / 2
    elif obj_B["rotation"]["z_angle"] == 270.0:
        x_1 = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        x_2 = obj_B["position"]["x"] - size_B["width"] / 2 - size_A["length"] / 2 
        y_1 = obj_B["position"]["y"] - size_B["length"] / 2 + size_A["width"] / 2 
        y_2 = obj_B["position"]["y"] + size_B["length"] / 2 - size_A["width"] / 2
    
    return (x_1, x_2, y_1, y_2, z_min, z_min)