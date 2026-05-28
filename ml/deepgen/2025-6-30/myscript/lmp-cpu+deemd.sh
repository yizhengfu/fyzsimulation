#!/bin/bash
#SBATCH -N 1
#SBATCH -o %j.out
#SBATCH -e %j.err
 
module purge
module load lmp-cpu+deepmd
 
# 线程控制

export OMP_NUM_THREADS=1
export DP_INTRA_OP_PARALLELISM_THREADS=1
export DP_INTER_OP_PARALLELISM_THREADS=1

# 串行处理输入文件
for in_file in in.*; do
    base_name="${in_file#in.}"
    echo "正在处理: ${in_file}"
    mpirun -np $SLURM_NTASKS lmp_mpi -in ${in_file} > ${base_name}.out 2>&1
    wait  # 确保任务完成后再继续
    echo "已完成: ${base_name}.out"
done
