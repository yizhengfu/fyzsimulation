import os

# 获取脚本所在文件夹的路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义输入和输出文件路径
input_file_path = os.path.join(script_dir, "spec.txt")
output_file_path = os.path.join(script_dir, "chanwu.txt")

# 读取输入文件内容
with open(input_file_path, 'r') as input_file:
    lines = input_file.readlines()

# 分割每行的数据并添加调试信息
data = []
for line in lines:
    line = line.strip()
    columns = line.split(';')
    data.append(columns)

# 提取倒数第三行的数值用于排序
last_row = data[-3]
sorting_indices = sorted(range(1, len(last_row)), key=lambda i: int(last_row[i]), reverse=True)

# 根据排序结果重新排列文件内容
sorted_data = []
for line in data:
    sorted_line = [line[0]] + [line[i] for i in sorting_indices]
    sorted_data.append(sorted_line)

# 输出前10列的内容到输出文件
with open(output_file_path, 'w') as output_file:
    for line in sorted_data:
        output_line = ';'.join(line[:10]) + '\n'
        output_file.write(output_line)

print(f"已完成排序并将内容保存到 {output_file_path}")
