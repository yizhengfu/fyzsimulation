import tkinter as tk
from tkinter import filedialog
import dpdata
import numpy as np


def process_data():
    folder_path = folder_path_entry.get()
    output_folder_path = output_folder_path_entry.get()

    try:
        # 读取 CP2K 的 AIMD 输出文件
        data = dpdata.LabeledSystem(folder_path, cp2k_output_name='Li3AL9B24.out', fmt='cp2kdata/md')


        # 获取用户输入的总帧数和验证数据帧数
        total_frames = int(total_frames_entry.get())
        validation_frames = int(validation_frames_entry.get())

        # 随机选取指定数量的帧作为验证数据，其余为训练数据
        index_validation = np.random.choice(total_frames, size=validation_frames, replace=False)
        index_training = list(set(range(total_frames)) - set(index_validation))
        data_training = data.sub_system(index_training)
        data_validation = data.sub_system(index_validation)

        # 将训练数据和验证数据输出到指定位置
        data_training.to_deepmd_npy(output_folder_path + '/training_data')
        data_validation.to_deepmd_npy(output_folder_path + '/validation_data')

        result_text.insert(tk.END, "Data processing successful!\n")
    except Exception as e:
        result_text.insert(tk.END, f'Error: {str(e)}\n')


# 创建主窗口
root = tk.Tk()
root.title("Data Processing GUI")

# 添加文件夹路径输入框和按钮
folder_path_label = tk.Label(root, text="Input Folder Path:")
folder_path_label.grid(row=0, column=0)

folder_path_entry = tk.Entry(root, width=50)
folder_path_entry.grid(row=0, column=1)

browse_button = tk.Button(root, text="Browse",
                          command=lambda: folder_path_entry.insert(tk.END, filedialog.askdirectory()))
browse_button.grid(row=0, column=2)

# 添加输出文件夹路径输入框和按钮
output_folder_path_label = tk.Label(root, text="Output Folder Path:")
output_folder_path_label.grid(row=1, column=0)

output_folder_path_entry = tk.Entry(root, width=50)
output_folder_path_entry.grid(row=1, column=1)

output_browse_button = tk.Button(root, text="Browse",
                                 command=lambda: output_folder_path_entry.insert(tk.END, filedialog.askdirectory()))
output_browse_button.grid(row=1, column=2)

# 添加输入总帧数的输入框和标签
total_frames_label = tk.Label(root, text="Total Frames:")
total_frames_label.grid(row=2, column=0)

total_frames_entry = tk.Entry(root, width=10)
total_frames_entry.grid(row=2, column=1)

# 添加选择验证数据帧数的输入框和标签
validation_frames_label = tk.Label(root, text="Validation Frames:")
validation_frames_label.grid(row=3, column=0)

validation_frames_entry = tk.Entry(root, width=10)
validation_frames_entry.grid(row=3, column=1)

# 添加处理按钮
process_button = tk.Button(root, text="Process Data", command=process_data)
process_button.grid(row=4, column=1)

# 添加处理结果显示文本框
result_text = tk.Text(root, height=15, width=60)
result_text.grid(row=5, columnspan=3)

root.mainloop()
