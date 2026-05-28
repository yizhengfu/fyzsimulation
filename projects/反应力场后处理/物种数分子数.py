import re


def main():
    # 读取文档
    with open("input.txt", 'r') as file:
        document_data = file.read().strip().split('\n')

    # 输出文档行数
    print(f"输入文件行数: {len(document_data)}")

    # 初始化计数器
    species_count = []
    molecule_sum = []

    # 打开输出文件
    with open("fenlie.txt", "w") as fenlie_file:
        for line in document_data[2:]:
            # 使用正则表达式提取非整数和小数部分
            data = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', line)

            # 跳过第一个元素，即第一列数据
            data = data[1:]

            # 计算该行数据中大于零的元素个数
            count = sum(1 for val in data if float(val) > 0)
            species_count.append(count)

            # 计算该行数据中大于零的元素总和，并将其转换为整数
            sum_val = int(sum(float(val) for val in data if float(val) > 0))
            molecule_sum.append(sum_val)

            # 将非整数和小数部分写入 "fenlie.txt" 文件
            fenlie_file.write(';'.join(data) + '\n')

    # 输出输出文件行数
    print(f"输出文件行数: {len(species_count)}")

    # 确保输出文件行数与输入文件相同
    num_lines = len(document_data) - 2  # 减去前两行
    with open("fenlie.txt", "a") as fenlie_file:
        fenlie_file.write(f"总行数: {num_lines}\n")

    # 将物种数和分子数保存到 "output.txt" 文件
    with open("output.txt", "w") as output_file:
        output_file.write("物种数列表:" + str(species_count) + "\n")
        output_file.write("分子数列表:" + str(molecule_sum) + "\n")


if __name__ == "__main__":
    main()
