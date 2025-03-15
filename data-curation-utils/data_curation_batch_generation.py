import os


slurm_template = """#!/bin/bash
#SBATCH --account=XX
#SBATCH --partition=gengpu
#SBATCH --gres=gpu:1
#SBATCH --job-name=d{start}_{end}
#SBATCH --output=logs/d{start}_{end}.out
#SBATCH --error=logs/data_curation_{start}_{end}.err
#SBATCH --time=2-00:00:00

conda activate idesign

python data_curation.py --start {start} --end {end}
"""


gap = 250
start_range = 0
end_range = 10000


slurm_dir = "data_curation_scripts"
os.makedirs(slurm_dir, exist_ok=True)


for start in range(start_range, end_range, gap):
    end = min(start + gap, end_range)  
    script_content = slurm_template.format(start=start, end=end)

    script_filename = f"{slurm_dir}/run_curation_{start}_{end}.sh"
    with open(script_filename, "w") as f:
        f.write(script_content)

print(f"Generated {end_range // gap} SLURM scripts in {slurm_dir}/")
