#!/bin/bash
#SBATCH --partition=sm
#SBATCH -N 1
#SBATCH -n 40
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:1
module purge 
module load openmpi/5.0.5 lammps/kokkos

for in_file in in.*; do
    base_name="${in_file#in.}"
    echo "正在处理: ${in_file}"
    mpirun -np $SLURM_NTASKS --bind-to none lmp_kokkos_cuda_mpi -k on gpu $j -sf kk -pk kokkos newton on neigh half -in ${in_file} > ${base_name}.out 2>&1 
    echo "已完成: ${base_name}.out"
done