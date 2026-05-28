#!/bin/bash
#SBATCH -N 1
#SBATCH --gres=gpu:1
#SBATCH -o %j.out
#SBATCH -e %j.err
module purge 
module load  anaconda/dp
conda activate base

for in_file in in.*; do
    base_name="${in_file#in.}"
    echo "正在处理: ${in_file}"
    lmp -in ${in_file} > ${base_name}.out 2>&1
    echo "已完成: ${base_name}.out"
done