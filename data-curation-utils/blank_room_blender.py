import bpy
import json
import os
import bmesh

def clear_scene():
    bpy.ops.object.select_all(action='DESELECT')  
    for obj in bpy.context.scene.objects:
        if obj.type != 'CAMERA':  
            obj.select_set(True)

    bpy.ops.object.delete()  

def add_light():
    light = bpy.data.objects.get("Main_Light")

    if light is None:
        light_data = bpy.data.lights.new(name="Main_Light", type='SUN')  # 太阳光
        light = bpy.data.objects.new(name="Main_Light", object_data=light_data)
        bpy.context.collection.objects.link(light)
    light.location = (5, -5, 10)  
    light.data.energy = 5  
    light.data.angle = 0.5  
    return light
    
def create_room(width, depth, height):
    # Create floor
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))

    # Extrude to create walls
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    bpy.ops.object.mode_set(mode='OBJECT')

    # Scale the walls to the desired dimensions
    bpy.ops.transform.resize(value=(width, depth, 1))

    bpy.context.active_object.location.x += width / 2
    bpy.context.active_object.location.y += depth / 2

file_path = "../generated_room_descriptions.json"
curated_data_path = "../curated_data"
with open(file_path, 'r') as f:
    rooms_data = json.load(f)

for i, room in enumerate(rooms_data):
    clear_scene()  
    add_light() 
    os.makedirs(f"{curated_data_path}/room_{i}", exist_ok=True)
    create_room(room["size"]["x"], room["size"]["y"], room["size"]["z"])

    room_path = f"{curated_data_path}/room_{i}"
    bpy.ops.wm.save_as_mainfile(filepath=room_path + "/generated_room_only.blend")

    scene = bpy.context.scene
    camera = bpy.data.objects.get("Camera")

    camera.data.type = 'PERSP'  
    camera.data.lens = 33  
    camera.data.lens_unit = 'MILLIMETERS'  
    camera.data.shift_x = 0.3 
    camera.data.shift_y = 0.2  
    scene.render.resolution_x = 500
    scene.render.resolution_y = 500 
    camera.data.clip_start = 0.1 
    camera.data.clip_end = 100.0  

    scene.render.filepath = room_path + "/render_output.png"
    scene.render.image_settings.file_format = 'PNG'

    bpy.ops.render.render(write_still=True) 

