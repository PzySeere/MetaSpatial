set -x

export VLLM_ATTENTION_BACKEND=XFORMERS
export VLLM_USE_V1=0

MODEL_PATH=Qwen/Qwen2.5-VL-7B-Instruct  # replace it with your local file path

SYSTEM_PROMPT="""You FIRST think about the reasoning process as an internal monologue and then provide the final answer.
 The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE put in <answer> </answer>."""

python3 -m verl.trainer.main \
    config=examples/config.yaml \
    algorithm.adv_estimator=reinforce_plus_plus \
    data.train_files=zhenyupan/3d_layout_reasoning@train \
    data.val_files=zhenyupan/3d_layout_reasoning@test \
    data.system_prompt="${SYSTEM_PROMPT}" \
    worker.actor.model.model_path=${MODEL_PATH} \
    worker.rollout.enable_chunked_prefill=false \
    trainer.experiment_name=qwen2_5_vl_7b_3d_reasoning_reinforce_pp \
    trainer.n_gpus_per_node=4 
