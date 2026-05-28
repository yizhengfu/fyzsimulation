#!/bin/bash
#SBATCH -N 1
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:1
module purge
module load lmp-gpu-kokkos+deepmd
# 线程控制
# 线程控制

export OMP_NUM_THREADS=1
export DP_INTRA_OP_PARALLELISM_THREADS=1
export DP_INTER_OP_PARALLELISM_THREADS=1

for in_file in in.*; do
    base_name="${in_file#in.}"
    echo "正在处理: ${in_file}"

    #srun -n $SLURM_NTASKS --mpi=pmi2 lmp_mpi -sf gpu -pk gpu 1 -in ${in_file} > ${base_name}.out 2>&1
    mpirun -np $SLURM_NTASKS lmp_mpi -sf gpu -pk gpu 1 -in ${in_file} > ${base_name}.out 2>&1
    # mpirun -np $SLURM_NTASKS lmp_kokkos_cuda_mpi -k on g 1 -sf kk -pk kokkos newton on neigh half -in ${in_file} > ${base_name}.out 2>&1
    # srun -n $SLURM_NTASKS --mpi=pmi2 lmp_kokkos_cuda_mpi -k on g 1 -sf kk -pk kokkos newton on neigh half -in ${in_file} > ${base_name}.out 2>&1
    wait  # 确保任务完成后再继续
    echo "已完成: ${base_name}.out"
done 