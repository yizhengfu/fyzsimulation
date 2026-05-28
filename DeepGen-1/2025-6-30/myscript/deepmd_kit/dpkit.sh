#!/bin/bash
#SBATCH --partition=smaster
#SBATCH -N 1
#SBATCH -n 2
#SBATCH --ntasks-per-node=2
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --gres=gpu:2
###########################
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/data/app/deepmd-gpu/3.0.3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/data/app/deepmd-gpu/3.0.3/etc/profile.d/conda.sh" ]; then
        . "/data/app/deepmd-gpu/3.0.3/etc/profile.d/conda.sh"
    else
        export PATH="/data/app/deepmd-gpu/3.0.3/bin:$PATH"
    fi
fi
unset __conda_setup
##########################
# <<< conda initialize <<<
dp train input.json
#dp train  --restart model.ckpt  input.json
#dp freeze -o graph.pb
#dp compress -i graph.pb -o graph-compress.pb