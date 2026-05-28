import pandas as pd
import openpyxl
import re

# 读取Excel文件
df = pd.read_excel('1.xlsx')

# 打开原始Excel文件
wb = openpyxl.load_workbook('1.xlsx')
ws = wb.active

# 处理每个组
for i in range(0, len(df), 2):
    group = df.iloc[i:i+2]

    # 计算并替换C的数目（只在奇数行进行操作）
    for j, row in group.iterrows():
        if j % 2 == 0:
            continue
        for col_num, cell_value in enumerate(row[3:], start=4):
            if pd.notna(cell_value):
                cell_text = str(cell_value)
                c_count = 0
                matches = re.findall(r'C(\d*)', cell_text)
                for match in matches:
                    if match:
                        c_count += int(match)
                    else:
                        c_count += 1
                cell_text = str(c_count)  # 替换文本为C数目的数字部分
                ws.cell(row=j+1, column=col_num, value=cell_text)

# 保存为新的Excel文件
wb.save('test.xlsx')
