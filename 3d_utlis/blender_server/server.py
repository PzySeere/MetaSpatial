import bpy
import json
import socket
import sys
import os
import time
import platform
import math
from mathutils import Vector

# Clear the default scene
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def process_request(data):
    """Process a rendering request"""
    try:
        # Clear the scene first
        clear_scene()
        
        # Extract parameters from the request
        params = json.loads(data)
        room_name = params.get('room_name')
        step_number = params.get('step_number')
        ground_truth = params.get('ground_truth')
        
        # Set up paths
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        rooms_folder = os.path.join(project_root, "3d_utlis", "data")
        room_path = os.path.join(rooms_folder, room_name)

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
            
            # Try multiple approaches to disable shadows for compatibility with different Blender versions
            try:
                mat.shadow_method = 'NONE'  # Older Blender versions
            except AttributeError:
                try:
                    room.visible_shadow = False  # Some newer versions
                except AttributeError:
                    try:
                        room.cast_shadow = False  # Another possibility
                    except AttributeError:
                        # If all else fails, just continue without setting shadow properties
                        pass
            
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

        file_path = room_path + "/scene_graph-backtracked.json"

        # if ground_truth:
        #     file_path = room_path + "/scene_graph-backtracked.json"
        # else:
        #     file_path = room_path + "/scene_graph-backtracked-updated.json"

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
            
            bpy.ops.object.join()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            
            joined_object = bpy.context.view_layer.objects.active
            if joined_object is not None:
                joined_object.name = empty_parent.name + "-joined"

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
            # print(f"Processing object: {OBJS.name}")
            # print(f"Extracted key: {OBJS.name.split('-')[0]}")
            # print(f"Available keys: {list(objects_in_room.keys())}")
            key_variants = [
                OBJS.name,                      
                OBJS.name.replace("-joined", ""),  
                OBJS.name.replace(".001", ""), 
                OBJS.name.replace(".002", ""),  
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

        bpy.ops.wm.save_as_mainfile(filepath=room_path + "/generated_scene_step_" + str(step_number) + ".blend", check_existing=False)

        scene = bpy.context.scene
        camera = bpy.data.objects.get("Camera")
        light_data = bpy.data.lights.new(name="Lamp", type='POINT')
        light_object = bpy.data.objects.new(name="Lamp", object_data=light_data)

        # Link the light to the scene
        bpy.context.collection.objects.link(light_object)

        # Set light energy (brightness)
        light_data.energy = 1000  # adjust as needed
        
        # Create camera if it doesn't exist
        if camera is None:
            bpy.ops.object.camera_add(location=(6, -6, 4))  # Moved further back and higher up
            camera = bpy.context.active_object
            camera.name = "Camera"
            camera.rotation_euler = (1, 0, 0.6)  # Adjusted angle to look at scene
        
        # Set camera as active camera
        scene.camera = camera

        # Position the light inside the room (room dimensions are 6.0 x 4.0 x 3.0)
        light_object.location = (3.0, 2.0, 2.5)  # Center of the room, slightly below ceiling
        
        camera.data.type = 'PERSP' 
        camera.data.lens = 35  # Wider lens angle (was 35)
        camera.data.lens_unit = 'MILLIMETERS'  
        # camera.data.shift_x = 0.0  # Removed shift to center the view
        camera.data.shift_x = 0.3 
        camera.data.shift_y = 0.1
        scene.render.resolution_x = 800
        scene.render.resolution_y = 800 
        camera.data.clip_start = 0.1 
        camera.data.clip_end = 100.0
        scene.eevee.taa_render_samples = 4


        if ground_truth:
            scene.render.filepath = room_path + "/render_output_groundtruth1.png"
        else:
            scene.render.filepath = room_path + "/render_output_step_" + str(step_number) + ".png"
        scene.render.image_settings.file_format = 'PNG'

        bpy.ops.render.render(write_still=True)
        
        return f"Rendered image saved to {scene.render.filepath}"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error processing request: {str(e)}\n{error_details}"

# Main server loop
print("Blender server is running. Press Ctrl+C to exit.")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Allow socket to be reused immediately after closing
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use. Another instance of the server may be running.")
            print("Please terminate any existing server processes before starting a new one.")
            print(f"You can use: lsof -i:{PORT} | grep LISTEN")
            print(f"Or: pkill -f 'blender_server.py'")
            sys.exit(1)
        else:
            raise
    s.listen()
    print(f"Blender server listening on {HOST}:{PORT}")
    
    # Set socket to non-blocking mode with a timeout
    s.settimeout(1.0)
    
    while True:
        try:
            # Accept connections with timeout to allow for keyboard interrupts
            try:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(4096).decode('utf-8')
                    if data:
                        result = process_request(data)
                        conn.sendall(result.encode('utf-8'))
            except socket.timeout:
                # This is expected, just continue the loop
                continue
                
        except KeyboardInterrupt:
            print("Server shutting down...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            # Don't exit on error, just continue listening
            time.sleep(1)