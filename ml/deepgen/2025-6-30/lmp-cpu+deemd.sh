#!/bin/bash
#SBATCH --partition=snode
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -o %j.out
#SBATCH -e %j.err
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TF_INTRA_OP_PARALLELISM_THREADS=1
export TF_INTER_OP_PARALLELISM_THREADS=1
export KMP_AFFINITY=granularity=fine,compact,1,0
module load lmp-cpu+deepmd
mpirun -np 48 lmp_mpi XXXXX
