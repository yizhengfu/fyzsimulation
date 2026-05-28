#!/bin/bash
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH -o %j.out
#SBATCH -e %j.err

PHYS_CORES=$(nproc)  # 测试单路 CPU 核心

# 循环遍历 GPU 数量，0 和 1
for gpu_count in 0 1; do
    for inp_file in *.inp; do
        base_name="${inp_file%.inp}"
        if [ $gpu_count -eq 0 ]; then
            resultfile="${base_name}_gpu0.txt"
        else
            resultfile="${base_name}_gpu1.txt"
        fi
        # 清空结果文件
        > "$resultfile"
        # 删除之前可能存在的输出文件和能量文件
        rm -f "${base_name}.out" "${base_name}.ener"

        for (( i=1; i<=PHYS_CORES; i++ )); do
            # 记录开始时间（纳秒级别）
            start_ns=$(date +%s%N)

            if [ $gpu_count -eq 0 ]; then
                # 不使用 GPU
                module purge
                module load  mkl cp2k/2024.3/cpu
                mpirun -np $i --bind-to core --map-by core:PE=1 \
                       -x MKL_THREADING_LAYER=INTEL \
                       cp2k.popt -i "$inp_file" > "${base_name}.out" 2>&1
            else
                # 使用 1 个 GPU
                module purge
                module load mkl cp2k/2024.3/gpu
                NUM_PROCESSES=1
                mpirun -np $i --bind-to core --map-by core:PE=1 \
                       -x MKL_THREADING_LAYER=INTEL \
                       -x CUDA_VISIBLE_DEVICES=0 \
                       cp2k.popt -i "$inp_file" > "${base_name}.out" 2>&1
            fi

            # 记录结束时间（纳秒级别）
            end_ns=$(date +%s%N)

            # 计算运行时间（纳秒转换为秒）
            compute_time=$(echo "scale=6; ($end_ns - $start_ns) / 1000000000" | bc)

            # 写入结果文件
            printf "%d CPU %d GPU: Time = %9.6f s\n" $i $gpu_count $compute_time >> "$resultfile"
        done

        # 按照时间从小到大排序结果文件
        sort -k7 -g -o "$resultfile" "$resultfile"
    done
done

# 合并并排序文件
for inp_file in *.inp; do
    base_name="${inp_file%.inp}"
    merged_resultfile="${base_name}_merged.txt"
    cat "${base_name}_gpu0.txt" "${base_name}_gpu1.txt" > "$merged_resultfile"
    sort -k7 -g -o "$merged_resultfile" "$merged_resultfile"
done