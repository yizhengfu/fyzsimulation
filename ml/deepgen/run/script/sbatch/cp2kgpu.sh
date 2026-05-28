#!/bin/bash
#SBATCH -N 1
#SBATCH -o %j.out
#SBATCH -e %j.err
module purge
module load mkl cp2k/2024.3/gpu

# 尝试减少进程数量，这里设置为 1
NUM_PROCESSES=1

for inp_file in *.inp; do
    base_name="${inp_file%.inp}"
    mpirun -np $NUM_PROCESSES --bind-to core --map-by core:PE=1 \
           -x MKL_THREADING_LAYER=INTEL \
           -x CUDA_VISIBLE_DEVICES=0 \
           cp2k.popt -i "$inp_file" > "${base_name}.out" 2>&1
done


                