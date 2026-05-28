#!/bin/bash
#SBATCH -J lammps_test
#SBATCH -N 2
#SBATCH -n 64
#SBATCH -p ty_public
#SBATCH -o logs/%j.out
#SBATCH -e logs/%j.out




module purge
module load compiler/intel/2017.5.239
module load mpi/intelmpi/2017.4.239
module load mathlib/fftw/3.3.8/double/intel



mpirun -np 64 lmp_cpu < /public/home/fyznuc/software/lammps-29Sep2021/bench/LMP-C/in-eq.txt
