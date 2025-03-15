import openshape
from huggingface_hub import hf_hub_download
import torch
import json
import numpy as np
import transformers
import threading
import multiprocessing
import sys, os, shutil
import objaverse
from torch.nn import functional as F
import re
import argparse
import time

parser = argparse.ArgumentParser(description="Process room design data in a given range.")
parser.add_argument("--start", type=int, required=True, help="Starting index of rooms to process")
parser.add_argument("--end", type=int, required=True, help="Ending index of rooms to process")
args = parser.parse_args()

#Print device
print("Device: ", torch.cuda.get_device_name(0))

# Load the Pointcloud Encoder
pc_encoder = openshape.load_pc_encoder('openshape-pointbert-vitg14-rgb')

# Get the pre-computed embeddings
meta = json.load(
    open(hf_hub_download("OpenShape/openshape-objaverse-embeddings", "objaverse_meta.json", token=True, repo_type='dataset', local_dir = "OpenShape-Embeddings"))
)

meta = {x['u']: x for x in meta['entries']}
deser = torch.load(
    hf_hub_download("OpenShape/openshape-objaverse-embeddings", "objaverse.pt", token=True, repo_type='dataset', local_dir = "OpenShape-Embeddings"), map_location='cpu'
)
us = deser['us']
feats = deser['feats']

def move_files(file_dict, destination_folder, id):
    os.makedirs(destination_folder, exist_ok=True)
    for item_id, file_path in file_dict.items():
        destination_path = f"{destination_folder}{id}.glb"

        shutil.move(file_path, destination_path)
        print(f"File {item_id} moved from {file_path} to {destination_path}")


def load_openclip():
    print("Locking...")
    sys.clip_move_lock = threading.Lock()
    print("Locked.")
    clip_model, clip_prep = transformers.CLIPModel.from_pretrained(
        "laion/CLIP-ViT-bigG-14-laion2B-39B-b160k",
        low_cpu_mem_usage=True, torch_dtype=half,
        offload_state_dict=True,
    ), transformers.CLIPProcessor.from_pretrained("laion/CLIP-ViT-bigG-14-laion2B-39B-b160k")
    if torch.cuda.is_available():
        with sys.clip_move_lock:
            clip_model.cuda()
    return clip_model, clip_prep

def retrieve(embedding, top, sim_th=0.0, filter_fn=None):
    sims = []
    embedding = F.normalize(embedding.detach().cpu(), dim=-1).squeeze()
    for chunk in torch.split(feats, 10240):
        sims.append(embedding @ F.normalize(chunk.float(), dim=-1).T)
    sims = torch.cat(sims)
    sims, idx = torch.sort(sims, descending=True)
    sim_mask = sims > sim_th
    sims = sims[sim_mask]
    idx = idx[sim_mask]
    results = []
    for i, sim in zip(idx, sims):
        if us[i] in meta:
            if filter_fn is None or filter_fn(meta[us[i]]):
                results.append(dict(meta[us[i]], sim=sim))
                if len(results) >= top:
                    break
    return results

def get_filter_fn():
    face_min = 0
    face_max = 34985808
    anim_min = 0
    anim_max = 563
    anim_n = not (anim_min > 0 or anim_max < 563)
    face_n = not (face_min > 0 or face_max < 34985808)
    filter_fn = lambda x: (
        (anim_n or anim_min <= x['anims'] <= anim_max)
        and (face_n or face_min <= x['faces'] <= face_max)
    )
    return filter_fn

def preprocess(input_string):
    wo_numericals = re.sub(r'\d', '', input_string)
    output = wo_numericals.replace("_", " ")
    return output

f32 = np.float32
half = torch.float16 if torch.cuda.is_available() else torch.bfloat16
clip_model, clip_prep = load_openclip()
torch.set_grad_enabled(False)

# file_path = "/projects/p32364/IDesign/curated_data/room_0/scene_graph-backtracked-updated.json"

#print the time

for i in range(args.start, args.end):
    room_path = os.path.join("/projects/p32364/Metaverse-R1/data/", "room_" + str(i))
    print("Processing room: ", room_path)
    file_path = room_path + "/scene_graph-backtracked.json"
    #if the file does not exist, skip
    if not os.path.exists(file_path):
        print("File does not exist: ", file_path)
        continue
    with open(file_path, "r") as file:
        objects_in_room = json.load(file)
    print("Retrieving objects...")
    for obj_in_room in objects_in_room:
        name = obj_in_room['new_object_id']
        asset_path = room_path + '/assets/' + name + '.glb'
        if os.path.exists(asset_path):
            print(f"Asset {name} already exists in {asset_path}")
            continue
        if "style" in obj_in_room and "material" in obj_in_room:
            style, material = obj_in_room['style'], obj_in_room["material"]
        else:
            continue
        text = preprocess("A high-poly " + obj_in_room['new_object_id']) + f" with {material} material and in {style} style, high quality"
        device = clip_model.device
        tn = clip_prep(
            text=[text], return_tensors='pt', truncation=True, max_length=76
        ).to(device)
        enc = clip_model.get_text_features(**tn).float().cpu()
        retrieved_obj = retrieve(enc, top=1, sim_th=0.1, filter_fn=get_filter_fn())[0]
        print("Retrieved object: ", retrieved_obj["u"])
        processes = multiprocessing.cpu_count()
        objaverse_objects = objaverse.load_objects(
            uids=[retrieved_obj['u']],
            download_processes=processes
        )
        destination_folder = os.path.join(room_path + '/assets/')
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        move_files(objaverse_objects, destination_folder, obj_in_room['new_object_id'])
        
print("Done.")