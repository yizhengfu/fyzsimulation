#!/bin/bash
#SBATCH -N 1
#SBATCH -o %j.out
#SBATCH -e %j.err
# 尝试减少进程数量，这里设置为 1
export OMP_NUM_THREADS=1
module purge
module load  mkl cp2k/2025.1/cpu

# 遍历所有inp文件
for inp_file in *.inp; do
    # 获取不带.inp后缀的文件名作为文件夹名
    base_name="${inp_file%.inp}"
    
    # 创建新文件夹
    mkdir -p "$base_name"
    
    # 复制inp文件到新文件夹
    cp "$inp_file" "$base_name/"
    
    # 如果存在coord.xyz文件，也复制到新文件夹
    if [ -f "coord.xyz" ]; then
        cp coord.xyz "$base_name/"
    fi
    
    # 进入新文件夹
    cd "$base_name"
    
    echo "Processing $inp_file in folder $base_name"
    
    # 运行计算，保持原有的MPI参数
    mpirun -np $SLURM_NTASKS \
        --bind-to none \
        -x MKL_THREADING_LAYER=INTEL \
        cp2k.psmp -i "$inp_file" > "${base_name}.out" 2>&1
    
    # 返回上级目录
    cd ..
    
    echo "Calculation completed for $inp_file"
done