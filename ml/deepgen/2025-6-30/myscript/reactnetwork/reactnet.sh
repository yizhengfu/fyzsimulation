#!/bin/bash

# 检查是否提供了-a参数（至少需要1个元素）
if [ $# -eq 0 ]; then
    echo "错误：请提供 -a 选项的参数（例如：./script.sh C C H C O N H N N O）"
    exit 1
fi

# 获取当前目录路径（避免相对路径问题）
current_dir=$(pwd)

# 使用find递归获取所有子目录（排除当前目录本身）
find "$current_dir" -type d | while read -r folder; do
    # 跳过当前目录本身（避免处理根目录）
    if [ "$folder" = "$current_dir" ]; then
        continue
    fi

    # 提取相对文件夹名（方便显示）
    folder_rel=$(realpath --relative-to="$current_dir" "$folder")
    
    # 进入目标文件夹（失败则跳过）
    if ! cd "$folder"; then
        echo "警告：无法进入文件夹 $folder_rel，跳过..."
        continue
    fi

    # 检查当前文件夹（不递归子文件夹）是否有.lammpstrj文件
    lammpstrj_files=$(find . -maxdepth 1 -name "*.lammpstrj" -print -quit)
    if [ -n "$lammpstrj_files" ]; then
        echo "正在处理文件夹：$folder_rel"
        
        # 执行命令（-a参数使用命令行输入的所有参数）
        reacnetgenerator --type dump -i *.lammpstrj -a "$@" --nohmm
        
        # 检查命令执行状态
        if [ $? -eq 0 ]; then
            echo "命令在 $folder_rel 执行成功"
        else
            echo "警告：命令在 $folder_rel 执行失败"
        fi
    else
        echo "文件夹 $folder_rel 中未找到 .lammpstrj 文件"
    fi

    # 返回原目录
    cd "$current_dir"
done

echo "所有文件夹处理完成"