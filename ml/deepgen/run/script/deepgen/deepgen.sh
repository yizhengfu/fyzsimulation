module load  anaconda/dp
conda activate base
nohup dpgen run param.json machine.json > dpgen.log 2>&1 &