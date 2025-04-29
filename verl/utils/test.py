import os
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoProcessor

from dataset import RLHFDataset, collate_fn  # 根据你的路径修改这个 import


def build_single_sample_batch(data: dict, tokenizer, processor) -> dict:
    dataset = RLHFDataset(
        data_path="",  # 占位，不会实际用到
        tokenizer=tokenizer,
        processor=processor,
        prompt_key="prompt",
        answer_key="answer",
        image_key="images",
        max_prompt_length=512,
        truncation="right",
        system_prompt=None,
        max_pixels=1024 * 1024,
        min_pixels=64 * 64,
    )
    # 覆盖内部 dataset
    dataset.dataset = Dataset.from_dict(data)
    return collate_fn([dataset[0]])


def test_single_sample_batch():
    # 替换为你本地的一张图片路径
    image_path = "/projects/p32364/MetaSpatial/curated_data/room_2121/render_output.png"
    assert os.path.exists(image_path), f"Image not found: {image_path}"

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # 构造一条测试数据
    data = {
        "prompt": ["Place a bed near the window."],
        "answer": ["The bed is now placed near the window."],
        "images": [[{"bytes": image_bytes, "path": os.path.basename(image_path)}]],
    }

    # 初始化 tokenizer 和 processor
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen-VL-Chat")

    # 构造 batch
    batch = build_single_sample_batch(data, tokenizer, processor)

    # 基本检查
    print("✅ Keys in batch:", batch.keys())
    assert "input_ids" in batch
    assert "attention_mask" in batch
    assert "position_ids" in batch
    assert "ground_truth" in batch
    assert batch["input_ids"].shape[0] == 1
    assert batch["attention_mask"].shape[0] == 1
    assert isinstance(batch["input_ids"], torch.Tensor)
    assert isinstance(batch["ground_truth"][0], str)

    print("🎉 Single sample batch is valid.")
    print("Decoded prompt:\n", tokenizer.decode(batch["input_ids"][0], skip_special_tokens=True))
    print("Ground truth:\n", batch["ground_truth"][0])


if __name__ == "__main__":
    test_single_sample_batch()
