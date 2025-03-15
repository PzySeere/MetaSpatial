#!/bin/bash

# ensure the script exists in the slurm_scripts directory
script_dir="data_curation_scripts"

if [ ! -d "$script_dir" ]; then
    echo "Error: Directory $script_dir does not exist!"
    exit 1
fi

# count the number of tasks to submit
num_jobs=$(ls -1 $script_dir/run_curation_*.sh 2>/dev/null | wc -l)
if [ "$num_jobs" -eq 0 ]; then
    echo "No sbatch files found in $script_dir/"
    exit 1
fi

echo "Found $num_jobs sbatch files in $script_dir/. Submitting jobs..."

# iterate over and submit all sbatch files
for script in $script_dir/run_curation_*.sh; do
    echo "Submitting: $script"
    sbatch "$script"
    sleep 1  # avoid submitting too many tasks in a short time, reduce scheduling pressure
done

echo "All jobs submitted!"
