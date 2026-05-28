import pandas as pd

# 读取指定目录下的rate.xlsx文件
input_file = r'F:\DillonHuang\GAP_DI\TDI\2000K\rate.xlsx'
output_file = r'F:\DillonHuang\GAP_DI\TDI\2000K\mainreac.xlsx'

# 读取Excel文件
df = pd.read_excel(input_file)

# 创建一个新的DataFrame，用于存放筛选后的数据
result_df = pd.DataFrame(columns=df.columns)

# 初始化变量，用于保存前一行数据
prev_row = None

for index, row in df.iterrows():
    # 如果prev_row不为空，表示已经读取了一行数据
    if prev_row is not None:
        # 获取前一行和当前行的第3列数据
        prev_value = prev_row.iloc[2]
        current_value = row.iloc[2]

        # 比较第3列的数据
        if prev_value == current_value:
            # 两行数据第3列相同，跳过这一组数据
            prev_row = None
        else:
            # 保留第3列数字较大的一行
            if prev_value > current_value:
                result_df = pd.concat([result_df, prev_row.to_frame().T], ignore_index=True)
                result_df.iloc[-1, 2] -= current_value  # 减去较小行的第3列数据
            else:
                result_df = pd.concat([result_df, row.to_frame().T], ignore_index=True)
                result_df.iloc[-1, 2] -= prev_value  # 减去较小行的第3列数据
            prev_row = None
    else:
        prev_row = row

# 保存结果到mianreac.xlsx
result_df.to_excel(output_file, index=False)
