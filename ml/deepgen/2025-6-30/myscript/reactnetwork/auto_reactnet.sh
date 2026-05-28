#!/bin/bash

# 检查是否提供了至少一个参数
if [ $# -lt 1 ]; then
    echo "用法: $0 \"<原子符号列表>\" [split参数] [reaction_mechanism参数]"
    echo "示例: $0 \"C H O\" \"1-20\" \"--detail\""
    exit 1
fi

# 参数定义
ATOM_SYMBOLS=$1       # 参数1: 原子符号列表 (用空格分隔)
SPLIT_PARAM=${2:-"1-10"}  # 参数2: split.py参数 (默认: 1-10)

# 步骤1: 主目录反应网络处理
cp /data/run/myscript/reactnetwork/reactnet.sh ./
chmod +x reactnet.sh
# 将原子符号列表作为多个独立参数传递
./reactnet.sh ${ATOM_SYMBOLS}

# 步骤2: 物种分析
cp /data/run/myscript/reactnetwork/species_analyzer.py ./
chmod +x species_analyzer.py
# 将原子符号作为多个独立参数传递
#python3 species_analyzer.py ${ATOM_SYMBOLS}
python3 species_analyzer.py 

# 步骤3: 轨迹切片
cp /data/run/myscript/reactnetwork/split.py ./
chmod +x split.py
# 传递split参数
python3 split.py ${SPLIT_PARAM}

# 步骤4: 再次反应网络处理处理
# mkdir -p reaction_mechanism
cd ./reaction_mechanism
cp /data/run/myscript/reactnetwork/reactnet.sh ./
chmod +x reactnet.sh
# 将原子符号作为多个独立参数传递
./reactnet.sh ${ATOM_SYMBOLS}

# 返回上级目录
cd ..

# 完成
echo "处理结束"