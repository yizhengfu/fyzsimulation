import openpyxl

# 指定输入文件和输出文件的路径
input_file_path = r"E:\N100\3500k\mianreac.xlsx"
output_file_path = r"E:\N100\\3500k\out.xlsx"

# 打开指定的xlsx文件
workbook = openpyxl.load_workbook(input_file_path)
sheet = workbook.active

# 指定要遍历的列（假设这里是第A列，你可以根据实际情况更改列号）
column_to_process = sheet['B']

# 遍历列中的单元格，进行文本替换
for cell in column_to_process:
    if cell.value is not None and "->" in cell.value:
        cell.value = cell.value.replace("->", "→")

# 保存修改后的数据到新的xlsx文件
workbook.save(output_file_path)

# 关闭工作簿
workbook.close()

print(f"处理完成，结果保存为 {output_file_path}")
