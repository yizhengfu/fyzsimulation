#!/bin/bash
# 将run中的步数设置为1即可
# 电脑最大核数,使用Linux自带的命令自动获取
maxcore=`cat /proc/cpuinfo | grep processor | wc -l` 

# 最大的GPU数目, 如果没有maxGPU会等于0
if command -v nvidia-smi &> /dev/null; then
  maxGPU=`nvidia-smi -L | grep GPU | wc -l`
else
  echo "NVIDIA driver not found, maxGPU set to 0"
  maxGPU=0
fi

for in_file in in.*; do
    base_name="${in_file#in.}"
    resultfile="${base_name}.txt"     # 测试结果文件的全名

# 清除可能存在的输出文件
rm $resultfile log.lammps

if [ "$maxGPU" -eq 0 ]; then              # 如果当前电脑没有GPU, 就这么计算
  for (( i=1; i<=$maxcore; i=i+1 )); do   # 以从1核到电脑最大的核心数提交任务

    # 以i个核并行运行lammps
    # mpirun -np $i $lammps -in $inputfile 

    module load oneapi/2021 lammps/deepmd-cpu
    mpirun -np $i lmp_mpi -in ${in_file} > ${base_name}.out 2>&1

    # 将结果输出到文件中, -n意思是不换行   
    echo -n "$i cores " >> $resultfile 
    # 将Performance这一行输出到结果文件中
    grep ^Performance: log.lammps >> $resultfile

  done

else  # 如果当前服务器的GPU数量不为0, 而且你的in文件里面涉及到的计算支持GPU加速  

  for (( j=1; j<=$maxGPU; j=j+1 )); do        # 外层循环是GPU数量
    for (( i=1; i<=$maxcore; i=i+1 )); do     # 内层循环是核心数量

      # 用i个核+j个GPU运行lammps执行对应的in文件
      # mpirun -np $i $lammps -in $inputfile -sf gpu -pk gpu $j
    module load oneapi/2021 lammps/deepmd
    mpirun -np $i lmp_mpi -sf gpu -pk gpu $j -in ${in_file} > ${base_name}.out 2>&1
      # 将结果输出到文件中, -n意思是不换行   
    echo -n "$i cores $j GPUs: " >> $resultfile 
      # 将Performance这一行输出到结果文件中
    grep ^Performance: log.lammps >> $resultfile
    done
  done
fi

# 将所有逗号替换为空格以便于后续排序处理
sed -i 's/,/ /g' $resultfile            

# 这里是对速度测试结果进行排序, -k8rn是组合选项, 需要拆开来逐个分析, 
# k意思是指定根据第几列的结果对每行文本进行排序, 后面跟一个4意思就是根据# 第8列的数据进行排序, r的意思是reverse, 修改排序顺序为从高到低, n的意思是根据第8个的字符串的具体数值来进行排序, -o的意思是在原文件的基础上进行排序, 不将结果输出到其他文件
if [ "$maxGPU" -eq 0 ]; then              # 如果没有GPU, 那么输出的格式是一种
  sort -k4rn -o $resultfile $resultfile
else                                      # 如果有GPU, 那么输出的格式是另一种
  sort -k8rn -o $resultfile $resultfile 
fi

done