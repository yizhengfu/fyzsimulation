import pandas as pd

# 读取Excel文件
df = pd.read_excel('test.xlsx')

# 删除奇数行的内容
df = df[df.index % 2 == 0]

# 重新排列表格
df.reset_index(drop=True, inplace=True)

# 将需要比较的列转换为数字类型（前三列不参与比较）
df[df.columns[3:]] = df[df.columns[3:]].apply(pd.to_numeric, errors='coerce')

# 定义一个函数来找出每一行的最大数字（前三列不参与比较）
def find_max(row):
    max_val = max(row[3:])  # 前三列不参与比较
    return max_val

# 添加新的列来存储最大数字
df['第四列'] = df.apply(find_max, axis=1)

# 将数据保存回Excel文件
df.to_excel('test_modified.xlsx', index=False)
