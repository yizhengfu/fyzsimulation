#!/bin/sh
#PBS -N try24  
#PBS -l nodes=1:ppn=24
#PBS -q batch
#PBS -e lmp2.err 
#PBS -o lmp2.out 
echo Time is `date`
echo Directory is `pwd`
echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR
NPROCS=`wc -l < ${PBS_NODEFILE}`
N_NODE=`uniq ${PBS_NODEFILE} | wc -l`
echo This job has allocated ${N_NODE} nodes with ${NPROCS} processors
echo Running on host `hostname`
echo This jobs runs on the following processors:
echo `cat $PBS_NODEFILE`
echo "**Start "
mpirun -np 24 lmp_mpi <in-eq1.txt
ecHo "**Finished !  "
