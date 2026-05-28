#!/bin/bash
#SBATCH -N 1

# 根据GPU存在性加载模块
module purge 
if command -v nvidia-smi &> /dev/null; then
    module load oneapi/2021 lammps/deepmd
else
    module load oneapi/2021 lammps/deepmd-cpu
fi

maxcore=$(nproc)  # 获取逻辑核心数
maxGPU=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)  # 获取GPU数量，若无则返回0

for in_file in in.*; do
    base_name="${in_file#in.}"
    resultfile="${base_name}.txt"
    > "$resultfile"  # 清空结果文件

    if [ "$maxGPU" -eq 0 ]; then
        # 无GPU时仅测试不同核心数
        for (( i=1; i<=maxcore/2; i++ )); do
            rm -f log.lammps
            mpirun -np "$i" lmp_mpi -in "$in_file" > "${base_name}.out" 2>&1
            echo -n "$i cores 0 GPUs: " >> "$resultfile"
            if grep -q ^Performance: log.lammps; then
                grep ^Performance: log.lammps | sed 's/,/ /g' >> "$resultfile"
            else
                echo "Performance: 0.0 tau/day 0.0 timesteps/s" >> "$resultfile"
            fi
        done
    else
        # 有GPU时测试不同核心和GPU组合
        for (( j=0; j<=maxGPU; j++ )); do
            for (( i=1; i<=maxcore/2; i++ )); do
                rm -f log.lammps
                if [ "$j" -eq 0 ]; then
                    # 不使用GPU
                    mpirun -np "$i" lmp_mpi -in "$in_file" > "${base_name}.out" 2>&1
                else
                    # 使用j个GPU
                    mpirun -np "$i" lmp_mpi -sf gpu -pk gpu "$j" -in "$in_file" > "${base_name}.out" 2>&1
                fi
                echo -n "$i cores $j GPUs: " >> "$resultfile"
                if grep -q ^Performance: log.lammps; then
                    grep ^Performance: log.lammps | sed 's/,/ /g' >> "$resultfile"
                else
                    echo "Performance: 0.0 tau/day 0.0 timesteps/s" >> "$resultfile"
                fi
            done
        done
    fi

    # 处理逗号并排序（假设timesteps/s在第8列）
    sed -i 's/,/ /g' $resultfile
    sort -k6rn -o $resultfile $resultfile
done