#!/bin/bash
#SBATCH -N 1
module purge 
# 统一模块加载逻辑
if command -v nvidia-smi &> /dev/null; then
    module purge
    module load openmpi/5.0.5 lammps/kokkos
    maxGPU=$(nvidia-smi -L | wc -l)
else
    module purge
    module load oneapi/2021 lammps/deepmd-cpu
    maxGPU=0
fi

maxcore=$(nproc)

for in_file in in.*; do
    base_name="${in_file#in.}"
    resultfile="${base_name}.txt"
    > "$resultfile"
    rm -f log.lammps ${base_name}.out  # 清理旧日志

    if [ "$maxGPU" -eq 0 ]; then
        # 纯CPU模式
        for (( i=1; i<=maxcore/2; i++ )); do
            mpirun -np "$i" lmp_mpi -in "$in_file" > "${base_name}.out" 2>&1
            echo -n "$i cores 0 GPUs: " >> "$resultfile"
            grep ^Performance: log.lammps | sed 's/,/ /g' >> "$resultfile" || echo "N/A" >> "$resultfile"
        done
    else
        # GPU模式（Kokkos）
        for (( j=1; j<=maxGPU; j++ )); do
            export CUDA_VISIBLE_DEVICES=$(seq -s "," 0 $((j-1)))  # 绑定具体GPU
            for (( i=1; i<=maxcore/2; i++ )); do
                mpirun -np "$i" lmp_kokkos_cuda_mpi \
                  -k on gpu $j -sf kk -pk kokkos newton on neigh half \
                  -in "$in_file" > "${base_name}.out" 2>&1
                echo -n "$i cores $j GPUs: " >> "$resultfile"
                grep ^Performance: log.lammps | sed 's/,/ /g' >> "$resultfile" || echo "N/A" >> "$resultfile"
            done
        done
    fi

    # 统一后处理
    sed -i 's/,/ /g' $resultfile
    sort -k6rn -o $resultfile $resultfile
done