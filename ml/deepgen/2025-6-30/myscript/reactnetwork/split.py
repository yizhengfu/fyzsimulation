import os
import shutil
import sys
import glob
import re

def create_folders_and_copy_content(input_file, output_folder, start_frame, end_frame):
    with open(input_file, 'r') as file:
        content = file.readlines()

    # 查找所有时间步的起始位置
    timestep_indices = [i for i, line in enumerate(content) if "ITEM: TIMESTEP" in line]

    # 如果没有足够的时间步（至少需要2个），则返回
    if len(timestep_indices) < 2:
        return 0

    processed_pairs = 0

    # 处理连续的时间步对
    for i in range(len(timestep_indices) - 1):
        start_index = timestep_indices[i]
        end_index = timestep_indices[i + 2] if (i + 2) < len(timestep_indices) else len(content)

        folder_name = str(i + 1)
        output_folder_path = os.path.join(output_folder, folder_name)
        os.makedirs(output_folder_path, exist_ok=True)

        # 修改输出文件后缀为.lammpstrj
        output_file_path = os.path.join(output_folder_path, 'trj.lammpstrj')
        with open(output_file_path, 'w') as output_file:
            # 写入当前时间步和下一个时间步的内容
            output_file.writelines(content[start_index:end_index])

        processed_pairs += 1

    # 删除不在范围内的帧文件夹
    for subdir in os.listdir(output_folder):
        subdir_path = os.path.join(output_folder, subdir)
        if os.path.isdir(subdir_path) and subdir.isdigit():
            frame_num = int(subdir)
            if frame_num < start_frame or frame_num > end_frame:
                shutil.rmtree(subdir_path)

    return processed_pairs

def should_skip_path(path, current_dir):
    """检查路径是否应该被跳过"""
    # 获取相对于当前目录的路径
    rel_path = os.path.relpath(path, current_dir)
    
    # 检查路径是否包含排除的文件夹
    exclude_folders = ["species_analysis", "reaction_mechanism"]
    for folder in exclude_folders:
        if folder in rel_path.split(os.sep):
            return True
    
    # 检查文件是否在排除的文件夹中
    for folder in exclude_folders:
        if folder in os.path.dirname(rel_path).split(os.sep):
            return True
    
    return False

def process_files(frame_range="1-10"):
    try:
        start_frame, end_frame = map(int, frame_range.split('-'))
    except ValueError:
        print("错误: 帧范围格式错误！请使用m-n格式（例如：1-10）")
        return

    # 获取当前工作目录
    current_dir = os.getcwd()
    output_main_folder = os.path.join(current_dir, "reaction_mechanism")
    os.makedirs(output_main_folder, exist_ok=True)

    processed_folders = 0
    processed_pairs = 0
    skipped_files = 0

    # 递归查找所有.lammpstrj文件
    lammpstrj_files = glob.glob(os.path.join(current_dir, "**", "*.lammpstrj"), recursive=True)
    
    if not lammpstrj_files:
        print("没有找到任何.lammpstrj文件！")
        return

    print(f"找到 {len(lammpstrj_files)} 个.lammpstrj文件")
    print(f"开始处理帧范围: {start_frame}-{end_frame}...")
    
    for input_file in lammpstrj_files:
        # 跳过排除的文件夹
        if should_skip_path(input_file, current_dir):
            skipped_files += 1
            print(f"跳过文件 (在排除文件夹中): {input_file}")
            continue
            
        # 获取相对路径
        rel_path = os.path.relpath(os.path.dirname(input_file), current_dir)
        
        # 创建输出子文件夹
        output_subfolder = os.path.join(output_main_folder, rel_path)
        os.makedirs(output_subfolder, exist_ok=True)
        
        # 处理文件
        print(f"处理文件: {input_file}")
        pairs = create_folders_and_copy_content(input_file, output_subfolder, start_frame, end_frame)
        
        if pairs > 0:
            processed_folders += 1
            processed_pairs += pairs
            print(f"  生成 {pairs} 个时间步对")
        else:
            skipped_files += 1
            print(f"  跳过 - 没有有效的连续时间步对")

    # 结果统计
    print("\n处理完成！")
    print(f"共处理了 {processed_folders} 个文件夹")
    print(f"生成了 {processed_pairs} 个时间步对")
    print(f"跳过了 {skipped_files} 个文件")
    print(f"输出目录: {output_main_folder}")

if __name__ == "__main__":
    # 解析命令行参数
    frame_range = "1-10"  # 默认帧范围
    
    if len(sys.argv) > 1:
        # 检查是否提供了帧范围参数
        if sys.argv[1].count('-') == 1:
            frame_range = sys.argv[1]
        else:
            print("警告: 无效的帧范围参数，使用默认值 1-10")
    
    print("=" * 50)
    print("轨迹文件分割处理器")
    print("=" * 50)
    print("处理当前目录及其所有子目录下的.lammpstrj文件")
    print("排除文件夹: species_analysis, reaction_mechanism")
    print(f"帧范围: {frame_range}")
    print("输出将保存到 reaction_mechanism 目录")
    print("=" * 50)
    
    process_files(frame_range)