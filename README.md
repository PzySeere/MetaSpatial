<div align="center">

# MetaSpatial: Reinforcing 3D Spatial Reasoning in VLMs for the Metaverse

[![arXiv](https://img.shields.io/badge/arXiv-2503.18470-ff0000.svg?style=for-the-badge)](https://arxiv.org/abs/2503.18470)  [![Github](https://img.shields.io/badge/MetaSpatial-000000?style=for-the-badge&logo=github&logoColor=000&logoColor=white)](https://github.com/PzySeere/MetaSpatial)  [![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)](https://github.com/PzySeere/MetaSpatial)  [![Hugging Face Collection](https://img.shields.io/badge/PRIME_Collection-fcd022?style=for-the-badge&logo=huggingface&logoColor=000)](https://huggingface.co/datasets/zhenyupan/3d_layout_reasoning)
</div>



<p align="center"><img src="assets/framework.png" width="700px" alt="MetaSpatial Framework" /></p>
<p align="center" style="font-size: 18px;">
<strong>MetaSpatial</strong> enhances spatial reasoning in VLMs using RL, internalizing 3D spatial reasoning to enable real-time 3D scene generation without hard-coded optimizations. By incorporating physics-aware constraints and rendering image evaluations, our framework optimizes layout coherence, physical consistency, and aesthetics. We provide an adaptive, efficient solution for applications in the metaverse, AR/VR, digital twins, and game development.    

<em>Our goal is to enable 3D spatial reasoning in the metaverse, where perfect ground truth doesn’t exist, making traditional SFT ineffective while RL naturally fits the task by learning from physics-aware constraints and adaptive rewards.</em>


</p>


## Preliminary Results
1. Both the 7B and 3B Qwen2.5 VLMs benefit from MetaSpatial, but the improvement is more pronounced in the 7B model. The 3B model still struggles with generating the correct output format, such as maintaining the same number and names of objects as the input and consistently providing x, y, and z positions for all objects.
<p align="center"><img src="assets/results-7b-3b.png" width="700px" alt="MetaSpatial Framework" /></p>

2. The results indicate that MetaSpatial improves both the 3B and 7B Qwen2.5-VL models, but the 7B model benefits more significantly, producing longer, more stable, and structured responses over time. The 3B model struggles with consistency, showing high variance in response length, with frequent fluctuations in both minimum and maximum lengths, suggesting difficulty in maintaining proper formatting (e.g., correct object count and structured spatial outputs). In contrast, the 7B model stabilizes its responses, reinforcing the observation that larger models adapt better to RL-based spatial reasoning tasks.
<p align="center"><img src="assets/results-7b-3b.png" width="700px" alt="response-length.png" /></p>

3. RL-Before vs RL-After: Enhancing 3D Spatial Reasoning with MetaSpatial.
The comparison between **RL-before** and **RL-after** highlights the effectiveness of **MetaSpatial's RL framework** in improving **3D spatial reasoning**. 

- **Before RL training**, object placements appear **disorganized, misaligned, and physically inconsistent**, with furniture often floating, overlapping, or placed in unrealistic configurations.  
- **After RL training**, the generated layouts become **more structured, realistic, and contextually coherent**, demonstrating improved **spatial awareness, object alignment, and functional arrangement**.  
- This reinforces the idea that **RL effectively optimizes VLMs for spatial reasoning**, enabling **more natural and practical 3D scene generation** for **the metaverse, AR/VR, and game development**.

<p align="center"><img src="assets/metaverse-before-after.png" width="700px" alt="Metaverse Before and After" /></p>

## Environments:
1. For data curation, we use the repository of IDesign: 
https://github.com/atcelen/IDesign/tree/main
```
cd IDesign
conda create -n idesign python=3.9
conda activate idesign
pip install -r requirements.txt
conda install pytorch==1.12.1 torchvision==0.13.1 torchaudio==0.12.1 cudatoolkit=11.3 -c pytorch
pip install -U git+https://github.com/NVIDIA/MinkowskiEngine
conda install -c dglteam/label/cu113 dgl
#sudo apt install -y libgl1-mesa-glx
pip install "numpy<2"
<!-- conda install sqlite=3.35.5 -->

#In IDesign/utils.py, comment the im.show() in function create_empty_image_with_boxes if you run the codes on server without GUI display.


pip install transformers objaverse accelerate
huggingface-cli login
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

git clone https://huggingface.co/OpenShape/openshape-demo-support
cd openshape-demo-support
pip install -e .
cd ..
```
2. For rendering, we use Blender:

    a. install blender-4.3.2-linux-x64

    b. create a python3.11 environment and activate it:
    ```bash
    conda create -n blender python=3.11
    conda activate blender
    ```
    c. install the blender python api:

    ```bash
    pip install bpy==4.3.0
    ```
3. For 3d assets retrieval, we install the OpenShape in the IDesign repository, please follow the instructions in the IDesign to install.

4. For R1 training, we install the EasyR1 repository, please follow the instructions in the EasyR1 to install: https://github.com/hiyouga/EasyR1

5. Remember to set the OPENAI_API_KEY in system environment variables.
## Data curation

#### 1. Generate the detailed description and size of a room by using "data-curation-utils/generate-room-json.py"

a. Change the openai api key in the script (line 7)

b. Change the output file path in the script (line 64)

c. Run the script and get **generated_room_descriptions.json**

#### 2. Gnerate the room only blend image by using "data-curation-utils/blank_room_blender.py"

##### !!!CHANGE Conda Env to the blender environment (which is python3.11 and has installed the bpy) before running this script!!! #####

a. Change the json file path of the generated room descriptions in the script (line 41)

b. Change the curated_data_path in the script (line 42). (This folder will store all rooms' data as individual folders named as room_0, room_1, etc.)

c. Run the script and get the room only blend image in each room's folder.

#### 3. Generate the scene graph of a room by using "data-curation-utils/data_curation.py"
In this step, we will use IDesign to generate the scene graph of a room.

a. Change the json file path of the generated room descriptions in the python file (line 14).

b. Change the curated_data_path in the python file (line 15). 

c1. You can directly run the python file to generate the scene graph of a room in each room's folder.

c2. You can also run the "data-curation-utils/data_curation_batch_generation.py" to generate **sbatch** scripts to generate the scene graphs parallelly.
    
    c2.1 Change the start and end of the range of rooms and how many rooms per sbatch would solve in line 18 - 20.
    c2.2 Change the path of the data_curation.py in **line 14** of "data_curation_batch_generation.py".
    c2.3 Change the output file path in the python file in **line 23** of "data_curation_batch_generation.py".
    c2.4 Run the "data_curation_batch_generation.py" to generate the sbatch scripts.
    c2.5 Change the script_dir in **line 4** of "data-curation-utils/data_curation_scripts_execute.sh" to the path of the sbatch scripts.
    c2.4 Run the "data-curation-utils/data_curation_scripts_execute.sh" to execute all the scripts automatically.

(ps: sometime for some rooms, the IDesign will stuck, so I set a limit time for each room. If the room is stuck more than 5 minutes, the scirpt will skip the room and continue to the next room. So, some rooms'folders will not have the scene graph after this step.)

#### 4. Retriever the 3d assets by using "data-curation-utils/retriever.py"

a. Change the folder path in **line 108** of retrieve.py. This folder includes all rooms' folders.

b. Change the retrieve.py file path in **line 15** of "retriever_batch_generation.py".

c. Change the start and end of the range of rooms and how many rooms per sbatch would solve in **line 18 - 20** of "retriever_batch_generation.py".

d. Change the generated sbatch scripts folder path in **line 22** of "retriever_batch_generation.py".

e. Run the "retriever_batch_generation.py" to generate the sbatch scripts.

f. Run all the sbatch scripts and wait.

#### 5. Summarize the all data and generate the dataset to update in huggingface.

a.  Change the room_description file path in **line 10** of "hf_data_curation.py".

b. Change the curated_data_path in **line 11** of "hf_data_curation.py".

c. Change the name of dataset and huggingface in **line 93, 96, 97, 98** of "hf_data_curation.py".

c. Run the "hf_data_curation.py" to summarize the all data and generate the dataset to update in huggingface.

## Training models
```
bash examples/run_qwen2_5_vl_7b_3d_reasoning.sh
```
## To Do

We plan to further improve and expand **MetaSpatial** with the following updates:

1. **Hyperparameter Optimization**: Due to computational constraints, our current results have not undergone thorough parameter tuning or hyperparameter selection. We will conduct additional experiments to identify the most effective configurations for training.
   
2. **Comparative Analysis of RL Algorithms**: We will provide more experimental results comparing different RL algorithms in terms of their effectiveness and stability, offering deeper insights into their impact on spatial reasoning.

3. **Multi-Turn Rollout Implementation**: Our current release only supports **single-turn rollouts**. We aim to enhance our framework by incorporating **multi-turn reasoning**, where the VLM refines its outputs iteratively by analyzing the rendered scene from generated coordinates, improving spatial coherence over multiple iterations.

4. **Comprehensive Report Paper**: We will soon release a more detailed report summarizing our findings, experimental results, and technical insights into **MetaSpatial**.

5. **Training Speed Optimization**: Due to time and resource constraints, development has been handled by few contributors. There are several potential optimizations to accelerate training, such as **replacing GPT-4o scoring with a locally deployed high-performance VLM**, exploring **faster rendering alternatives to Blender**, and refining the overall pipeline for **more efficient computation**.

Stay tuned for updates as we continue to refine and expand the capabilities of **MetaSpatial**!

## Contributors
**[Zhenyu Pan](https://pzyseere.github.io/)**, **[Han Liu](https://magics.cs.northwestern.edu/people.html)**


## Acknowledgements

This work builds upon the codebases of **[VERL](https://github.com/volcengine/verl)** and **[EasyR1](https://github.com/hiyouga/EasyR1)**, extending their foundations to enhance 3D spatial reasoning in VLMs. We sincerely appreciate the EasyR1 development team for their generous support and insightful guidance throughout our implementation process. Additionally, this project was inspired by **[RAGEN](https://github.com/ZihanWang314/ragen)**, who provides valuable insights into the adaptation of PPO for new tasks. Their work contributed to our understanding of **reinforcement learning strategies** in this context. We would also like to express our gratitude to **[Zhuo Liu](https://joeliuz6.github.io/)** for the valuable discussions that contributed to this work. Furthermore, we sincerely appreciate **[IDesign](https://github.com/atcelen/IDesign)** for providing an excellent code framework that facilitated the generation of our dataset.

## Citation
If you find this work useful, please consider give us a star! Also, please consider citing:
```md
@misc{pan2025metaspatialreinforcing3dspatial,
      title={MetaSpatial: Reinforcing 3D Spatial Reasoning in VLMs for the Metaverse}, 
      author={Zhenyu Pan and Han Liu},
      year={2025},
      eprint={2503.18470},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2503.18470}, 
}
```



