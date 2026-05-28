#!/bin/bash
#SBATCH -N 1
#SBATCH -o %j.out
#SBATCH -e %j.err
module purge 
module load oneapi/2021 lammps/deepmd-cpu
for in_file in in.*; do
    base_name="${in_file#in.}"
    echo "正在处理: ${in_file}"
    mpirun -np $SLURM_NTASKS lmp_mpi -in ${in_file} > ${base_name}.out 2>&1 
    echo "已完成: ${base_name}.out"
done
