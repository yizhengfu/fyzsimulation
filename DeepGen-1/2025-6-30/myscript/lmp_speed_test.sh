#!/bin/bash
#SBATCH -N 1

# 根据GPU存在性加载模块
if command -v nvidia-smi &> /dev/null; then
    module purge
    module load lmp-cpu+deepmd
    export OMP_NUM_THREADS=1
    export DP_INTRA_OP_PARALLELISM_THREADS=1
    export DP_INTER_OP_PARALLELISM_THREADS=1
    export KMP_BLOCKTIME=0
    export KMP_AFFINITY=granularity=fine,compact,1,0
else
    module purge
    module load lmp-gpu-kokkos+deepmd
    export OMP_NUM_THREADS=1
    export DP_INTRA_OP_PARALLELISM_THREADS=1
    export DP_INTER_OP_PARALLELISM_THREADS=1
    export KMP_BLOCKTIME=0
    export KMP_AFFINITY=granularity=fine,compact,1,0

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
            srun -np "$i" --mpi=pmi2 lmp_mpi -in ${in_file} > ${base_name}.out 2>&1           
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
                    srun -np "$i" --mpi=pmi2 lmp_mpi -in ${in_file} > ${base_name}.out 2>&1 
                else
                    # 使用j个GPU
                    srun -n "$i" --mpi=pmi2 lmp_mpi -sf gpu -pk gpu "$j" -in ${in_file} > ${base_name}.out 2>&1 

                   # mpirun -np "$i" lmp_kokkos_cuda_mpi -k on g "$j" -sf kk -pk kokkos newton on neigh half -in ${in_file} > ${base_name}.out 2>&1
                    # 注意双引号mpirun -np "$i" lmp_mpi -sf gpu -pk gpu "$j" -in "$in_file" > "${base_name}.out" 2>&1
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