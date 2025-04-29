import os
from PIL import Image
from datasets import Dataset, Features, Value, Image as HFImage
from verl.utils.dataset import RLHFDataset, collate_fn
from transformers import AutoTokenizer, AutoProcessor
image_path = "/projects/p32364/MetaSpatial/curated_data/room_2121/render_output.png"
prompt = "Place a bed near the window."
answer = "The bed is now placed near the window."

room_image = Image.open(image_path).convert("RGB")
data = [{
    "problem": prompt,
    "answer": answer,
    "images": [room_image], 
}]
features = Features({
    "problem": Value("string"),
    "answer": Value("string"),
    "images": [HFImage()] 
})
dataset = Dataset.from_list(data, features=features)
save_dir = "./test_single_sample"
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, "train.parquet")
dataset.to_parquet(save_path)
print(f"✅ Saved parquet to {save_dir}")
# test_dir = "/scratch/upw2709/hf/cache/datasets--zhenyupan--3d_layout_reasoning/snapshots/6f2151de5840f2080cf0c6ad4100f37e411c9a5f/data/train-00000-of-00001.parquet"
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", trust_remote_code=True)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", trust_remote_code=True)

dataset = RLHFDataset(
    data_path=save_path,
    tokenizer=tokenizer,
    processor=processor,
    prompt_key="problem",
    answer_key="answer",
    image_key="images",
    max_prompt_length=512,
    truncation="right",
    max_pixels=1024 * 1024,
    min_pixels=64 * 64,
)

sample = dataset[0]
batch = collate_fn([sample])