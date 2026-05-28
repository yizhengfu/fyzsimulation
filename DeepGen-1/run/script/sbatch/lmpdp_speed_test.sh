#!/bin/bash
#SBATCH -N 1
#SBATCH --gres=gpu:0
#SBATCH -o %j.out
#SBATCH -e %j.err
module purge 
module load  anaconda/dp
conda activate base
maxcore=$(nproc)
maxGPU=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)
for in_file in in.*; do
    base_name="${in_file#in.}"
    resultfile="${base_name}.txt"
    # 清空结果文件
    > $resultfile
    # 清除可能存在的输出文件
     rm log.lammps
    # 测试 GPU 为 0 的情况
    for (( i=1; i<=$maxcore; i++ )); do
        lmp -in ${in_file} > ${base_name}.out 2>&1
        perf_info=$(grep ^Performance: log.lammps)
        if [ -n "$perf_info" ]; then
            echo "$i cores 0 gpu $perf_info" >> $resultfile
        fi
    done
    # 测试 GPU 为 1 的情况
    for (( i=1; i<=$maxcore; i++ )); do
        lmp -in ${in_file} > ${base_name}.out 2>&1
        perf_info=$(grep ^Performance: log.lammps)
        if [ -n "$perf_info" ]; then
            echo "$i cores 1 gpu $perf_info" >> $resultfile
        fi
    done
    # 将所有逗号替换为空格以便于后续排序处理
    sed -i 's/,/ /g' $resultfile
    sort -k6rn -o $resultfile $resultfile
done