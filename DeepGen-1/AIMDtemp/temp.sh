#!/bin/bash

#!/bin/sh
#SBATCH -N 1
#SBATCH -n 28
#SBATCH -p normal,normal2,normal3,normal4
#SBATCH --ntasks-per-node=28
#SBATCH --output=%j.out
#SBATCH --error=%j.err
ulimit -s unlimited


source ~/env.sh

bash AIMD.sh
