import bpy
import json
import math
import os
import argparse
from distutils.util import strtobool  # parse "true"/"false" to bool
bpy.context.preferences.filepaths.save_version = 0  

parser = argparse.ArgumentParser(description="Process room design data in a given range.")
parser.add_argument("--room_name", type=str, required=True, help="Room name to process")
parser.add_argument("--step_number", type=int, required=True, help="Step number to process")
parser.add_argument("--ground_truth", type=lambda x: bool(strtobool(x)), required=True, help="Ground truth or not")
args = parser.parse_args()
room_path = os.path.join("/projects/p32364/MetaSpatial/curated_data", args.room_name)
ground_truth = args.ground_truth

object_name = 'Cube'
object_to_delete = bpy.data.objects.get(object_name)

# Check if the object exists before trying to delete it
if object_to_delete is not None:
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def import_glb(file_path, object_name):
    bpy.ops.import_scene.gltf(filepath=file_path)
    imported_object = bpy.context.view_layer.objects.active
    if imported_object is not None:
        imported_object.name = object_name
def create_room(width, depth, height):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(width / 2, depth / 2, height / 2))
    bpy.ops.transform.resize(value=(width, depth, height))

    room = bpy.context.active_object


    mat = bpy.data.materials.new(name="TransparentMaterial")
    mat.use_nodes = True  

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Alpha"].default_value = 0.2  

    mat.blend_method = 'BLEND'
    mat.shadow_method = 'NONE'
    room.data.materials.append(mat)

def find_glb_files(directory):
    glb_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".glb"):
                key = file.split(".")[0]
                if key not in glb_files:
                    glb_files[key] = os.path.join(root, file)
    return glb_files

def get_highest_parent_objects():
    highest_parent_objects = []

    for obj in bpy.data.objects:
        # Check if the object has no parent
        if obj.parent is None:
            highest_parent_objects.append(obj)
    return highest_parent_objects

def delete_empty_objects():
    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is empty (has no geometry)
        print(obj.name, obj.type)
        if obj.type == 'EMPTY':
            bpy.context.view_layer.objects.active = obj
            bpy.data.objects.remove(obj)

def select_meshes_under_empty(empty_object_name):
    # Get the empty object
    empty_object = bpy.data.objects.get(empty_object_name)
    # print(empty_object is not None)
    if empty_object is not None and empty_object.type == 'EMPTY':
        # Iterate through the children of the empty object
        for child in empty_object.children:
            # Check if the child is a mesh
            if child.type == 'MESH':
                # Select the mesh
                child.select_set(True)
                bpy.context.view_layer.objects.active = child
            else:
                select_meshes_under_empty(child.name)

def rescale_object(obj, scale):
    # Ensure the object has a mesh data
    if obj.type == 'MESH':
        bbox_dimensions = obj.dimensions
        scale_factors = (
                         scale["length"] / bbox_dimensions.x, 
                         scale["width"] / bbox_dimensions.y, 
                         scale["height"] / bbox_dimensions.z
                        )
        obj.scale = scale_factors


objects_in_room = {}

if args.ground_truth:
    file_path = room_path + "/scene_graph-backtracked.json"
else:
    file_path = room_path + "/scene_graph-backtracked-updated.json"

with open(file_path, 'r') as file:
    data = json.load(file)
    for item in data:
        if item["new_object_id"] not in ["south_wall", "north_wall", "east_wall", "west_wall", "middle of the room", "ceiling"]:
            objects_in_room[item["new_object_id"]] = item
print('============')
print(objects_in_room)
print('!!!!!!!!!!!!')

directory_path = room_path + "/assets"
glb_file_paths = find_glb_files(directory_path)

for item_id, object_in_room in objects_in_room.items():
    glb_file_path = os.path.join(directory_path, glb_file_paths[item_id])
    import_glb(glb_file_path, item_id)

parents = get_highest_parent_objects()
empty_parents = [parent for parent in parents if parent.type == "EMPTY"]
# print(empty_parents)

for empty_parent in empty_parents:
    bpy.ops.object.select_all(action='DESELECT')
    select_meshes_under_empty(empty_parent.name)
    
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not selected_meshes:
        print(f"Skipping join: No mesh objects under {empty_parent.name}")
        continue
        
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    joined_object = bpy.context.view_layer.objects.active
    if joined_object is None:
        print(f"Warning: No activate object after join for {empty_parent.name}")
        continue
    if joined_object.type != 'MESH':
        print(f"Warning: joined_object {joined_object.name} is not a mesh! Skipping renaming.")
        continue
    
    # rename the object
    print(f"Before renaming, joined object name: {joined_object.name}")
    joined_object.name = empty_parent.name + "-joined"
    print(f"After renaming, joined object name: {joined_object.name}")
    

bpy.context.view_layer.objects.active = None

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
for OBJS in MSH_OBJS:
    bpy.context.view_layer.objects.active = OBJS
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    OBJS.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = OBJS
    OBJS.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
# print('============')
# print(MSH_OBJS)
# print('============')
for OBJS in MSH_OBJS:
    print(f"Processing object: {OBJS.name}")
    print(f"Extracted key: {OBJS.name.split('-')[0]}")
    print(f"Available keys: {list(objects_in_room.keys())}")
    key_variants = [
        OBJS.name,                      # original name
        OBJS.name.replace("-joined", ""),  # remove "-joined"
        OBJS.name.replace(".001", ""),  # remove ".001"
        OBJS.name.replace(".002", ""),  # remove ".002"
    ]
    key = next((k for k in key_variants if k in objects_in_room), None)
    if key is None:
        print(f"Warning: No matching key found for {OBJS.name}")
        continue
    item = objects_in_room[key]
    object_position = (item["position"]["x"], item["position"]["y"], item["position"]["z"])  # X, Y, and Z coordinates
    object_rotation_z = (item["rotation"]["z_angle"] / 180.0) * math.pi + math.pi # Rotation angles in radians around the X, Y, and Z axes
    
    bpy.ops.object.select_all(action='DESELECT')
    OBJS.select_set(True)
    OBJS.location = object_position
    bpy.ops.transform.rotate(value=object_rotation_z,  orient_axis='Z')
    rescale_object(OBJS, item["size_in_meters"])

bpy.ops.object.select_all(action='DESELECT')
delete_empty_objects()

# TODO: Generate the room with the room dimensions
create_room(6.0, 4.0, 3)

# if args.ground_truth:
#     bpy.ops.wm.save_as_mainfile(filepath=room_path + "/generated_scene_groundtruth.blend", check_existing=False)
# else:
#     bpy.ops.wm.save_as_mainfile(filepath=room_path + "/generated_scene_step_" + str(args.step_number) + ".blend", check_existing=False)

scene = bpy.context.scene
camera = bpy.data.objects.get("Camera")
camera.data.type = 'PERSP' 
camera.data.lens = 35  
camera.data.lens_unit = 'MILLIMETERS'  
camera.data.shift_x = 0.3 
camera.data.shift_y = 0.1  
scene.render.resolution_x = 350
scene.render.resolution_y = 350 
camera.data.clip_start = 0.1 
camera.data.clip_end = 100.0  

# set the render path and image format
if args.ground_truth:
    scene.render.filepath = room_path + "/render_output_groundtruth.png"
else:
    scene.render.filepath = room_path + "/render_output_step_" + str(args.step_number) + ".png"
scene.render.image_settings.file_format = 'PNG'

# render and save the image
bpy.ops.render.render(write_still=True) 
