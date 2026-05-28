#!/bin/bash
#SBATCH --partition=sm
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:1
module load  anaconda/dp
conda activate base
dp train input.json
#dp train  --restart model.ckpt  input.json
dp freeze -o graph.pb
dp compress -i graph.pb -o graph-compress.pb
