import tkinter as tk
from tkinter import filedialog
import pandas as pd

def search_and_extract_excel(filename, search_string):
    # 读取 Excel 文件
    df = pd.read_excel(filename, header=None)

    # 初始化结果列表
    results = []

    # 遍历每一行
    for index, row in df.iterrows():
        row_result = 0  # 初始化行的结果

        # 遍历每一列
        for col_index, cell_value in enumerate(row):
            # 将每个单元格的内容作为检索目标
            target = str(cell_value)

            # 如果目标与搜索字符串完全相同
            if target == search_string:
                # 获取目标单元格后一格的数字，如果没有则记为0
                row_result = int(row[col_index + 1]) if col_index + 1 < len(row) else 0
                break  # 找到了相同内容，不需要再继续搜索

        # 将行的结果添加到列表
        results.append(row_result)

    # 返回结果
    return results

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    entry_path.delete(0, tk.END)
    entry_path.insert(0, filename)

def execute_search():
    filename = entry_path.get()
    search_string = entry_search.get()

    if filename and search_string:
        results = search_and_extract_excel(filename, search_string)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)

        for result in results:
            result_text.insert(tk.END, str(result) + "\n")

        result_text.config(state=tk.DISABLED)

# 创建主窗口
root = tk.Tk()
root.title("Excel Search Tool")

# 添加文件选择按钮
button_browse = tk.Button(root, text="Browse", command=browse_file)
button_browse.pack()

# 添加文件路径输入框
entry_path = tk.Entry(root, width=50)
entry_path.pack()

# 添加搜索字符串输入框
label_search = tk.Label(root, text="Search String:")
label_search.pack()

entry_search = tk.Entry(root, width=50)
entry_search.pack()

# 添加执行搜索按钮
button_search = tk.Button(root, text="Search", command=execute_search)
button_search.pack()

# 添加结果显示文本框
result_text = tk.Text(root, height=10, width=50, state=tk.DISABLED)
result_text.pack()

# 启动主循环
root.mainloop()
