import pandas as pd

# 读取文本文件并按分号分列
with open(r'E:\N100\N-100_RE\jili\reac.txt', 'r') as file:
    lines = file.readlines()

# 分列：将文件内容按分号分列
table = [line.strip().split(';') for line in lines]

# 使用Pandas创建DataFrame
df = pd.DataFrame(table)

# 输入表头信息
header = "R111"

# 查找表头所在列的索引
header_index = None
if header in df.iloc[0].values:
    header_index = df.iloc[0].values.tolist().index(header)

# 如果找到表头，继续处理
if header_index is not None:
    # 设置DataFrame的列名为第一行的内容
    df.columns = df.iloc[0]

    # 删除第一行（表头）
    df = df.iloc[1:]

    # 获取对应列的数据
    column = df.iloc[:, header_index]

    # 初始化变量来存储结果
    first_positive_row = None
    first_negative_row = None
    last_positive_row = None
    last_negative_row = None

    # 从上往下搜索第一个正数和第一个负数以及它们所在行的第一列信息
    for index, value in enumerate(column):
        try:
            numeric_value = float(value)
            if numeric_value > 0:
                if first_positive_row is None:
                    first_positive_row = df.iloc[index]
                last_positive_row = df.iloc[index]
            elif numeric_value < 0:
                if first_negative_row is None:
                    first_negative_row = df.iloc[index]
        except ValueError:
            pass

    # 从下往上搜索第一个正数和第一个负数以及它们所在行的第一列信息
    for index, value in reversed(list(enumerate(column))):
        try:
            numeric_value = float(value)
            if numeric_value > 0 and last_positive_row is None:
                last_positive_row = df.iloc[index]
            elif numeric_value < 0 and last_negative_row is None:
                last_negative_row = df.iloc[index]
        except ValueError:
            pass

    # 输出信息
    if first_positive_row is not None:
        print("第一个正数所在行的第一列信息:", first_positive_row.iloc[0])
    else:
        print("未找到正数")

    if last_positive_row is not None:
        print("最后一个正数所在行的第一列信息:", last_positive_row.iloc[0])
    else:
        print("未找到正数")

    if first_negative_row is not None:
        print("第一个负数所在行的第一列信息:", first_negative_row.iloc[0])
    else:
        print("未找到负数")

    if last_negative_row is not None:
        print("最后一个负数所在行的第一列信息:", last_negative_row.iloc[0])
    else:
        print("未找到负数")
else:
    print(f"未找到表头: {header}")
