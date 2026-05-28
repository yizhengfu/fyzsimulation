#!/bin/bash
#SBATCH --partition=smaster
#SBATCH -N 1
#SBATCH -n 2
#SBATCH --ntasks-per-node=2
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:1
module load lmp-gpu-kokkos+deepmd
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TF_INTRA_OP_PARALLELISM_THREADS=1
export TF_INTER_OP_PARALLELISM_THREADS=1
export KMP_AFFINITY=granularity=fine,compact,1,0
mpirun -np 2 lmp_mpi -sf gpu -pk gpu 1 -in XXXX
#或mpirun -np 2 lmp_kokkos_cuda_mpi -k on g 1 -sf kk -pk kokkos newton on neigh half -in XXXXX
