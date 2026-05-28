#!/bin/bash
#SBATCH --partition=sm
#SBATCH -N 1
#SBATCH -n 80
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:1
module load  oneapi/2021  lammps/deepmd
mpirun -np 80 lmp_mpi -sf gpu -pk gpu 1 -in in.lmp

