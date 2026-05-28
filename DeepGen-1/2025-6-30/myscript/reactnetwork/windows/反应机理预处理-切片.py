import os
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import re
import glob


def create_folders_and_copy_content(input_file, output_folder, start_frame, end_frame):
    with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
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
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
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


def should_skip_path(path, base_dir):
    """检查路径是否应该被跳过"""
    # 获取相对于基础目录的路径
    rel_path = os.path.relpath(path, base_dir)

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


def browse_input_folder():
    folder_path = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_path)
    update_status(f"已选择文件夹: {folder_path}")


def process_files():
    input_folder = input_folder_entry.get()
    frame_range = frame_range_entry.get()

    if not input_folder:
        messagebox.showerror("错误", "请先选择输入文件夹！")
        return

    try:
        start_frame, end_frame = map(int, frame_range.split('-'))
    except ValueError:
        messagebox.showerror("错误", "帧范围格式错误！请使用m-n格式（例如：1-10）")
        return

    output_main_folder = os.path.join(input_folder, "reaction_mechanism")
    os.makedirs(output_main_folder, exist_ok=True)

    processed_files = 0
    processed_pairs = 0
    skipped_files = 0

    # 递归查找所有.lammpstrj文件
    lammpstrj_files = glob.glob(os.path.join(input_folder, "**", "*.lammpstrj"), recursive=True)

    if not lammpstrj_files:
        messagebox.showinfo("完成", "没有找到任何.lammpstrj文件！")
        return

    # 创建进度窗口
    progress_window = tk.Toplevel(app)
    progress_window.title("处理进度")
    progress_window.geometry("400x200")
    progress_window.resizable(False, False)

    tk.Label(progress_window, text="处理进度:", font=("Arial", 10)).pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=len(lammpstrj_files))
    progress_bar.pack(fill=tk.X, padx=20, pady=10)

    status_label = tk.Label(progress_window, text=f"0/{len(lammpstrj_files)} 文件已处理", font=("Arial", 9))
    status_label.pack(pady=10)

    current_file_label = tk.Label(progress_window, text="", font=("Arial", 9), wraplength=380)
    current_file_label.pack(pady=5)

    # 强制更新窗口
    progress_window.update()

    # 处理每个文件
    for i, input_file in enumerate(lammpstrj_files):
        # 更新进度
        progress_var.set(i + 1)
        status_label.config(text=f"{i + 1}/{len(lammpstrj_files)} 文件已处理")
        current_file_label.config(text=f"正在处理: {os.path.basename(input_file)}")
        progress_window.update()

        # 跳过排除的文件夹
        if should_skip_path(input_file, input_folder):
            skipped_files += 1
            continue

        # 获取相对路径
        rel_path = os.path.relpath(os.path.dirname(input_file), input_folder)

        # 创建输出子文件夹
        output_subfolder = os.path.join(output_main_folder, rel_path)
        os.makedirs(output_subfolder, exist_ok=True)

        # 处理文件
        pairs = create_folders_and_copy_content(input_file, output_subfolder, start_frame, end_frame)

        if pairs > 0:
            processed_files += 1
            processed_pairs += pairs
        else:
            skipped_files += 1

    # 关闭进度窗口
    progress_window.destroy()

    # 显示结果
    if processed_files == 0:
        messagebox.showinfo("完成", "没有找到任何需要处理的文件！")
    elif processed_pairs == 0:
        messagebox.showinfo("完成", "没有找到任何有效的连续时间步对！")
    else:
        message = f"处理完成！\n共处理了 {processed_files} 个文件，生成 {processed_pairs} 个时间步对。\n跳过了 {skipped_files} 个文件。\n输出目录: {output_main_folder}"
        messagebox.showinfo("成功", message)
        # 打开输出文件夹（Linux系统使用xdg-open）
        if os.path.exists(output_main_folder):
            try:
                os.system(f"xdg-open '{output_main_folder}'")
            except Exception as e:
                messagebox.showwarning("提示", f"无法自动打开文件夹，请手动查看: {output_main_folder}")


def update_status(message):
    status_label.config(text=message)
    app.update()


# GUI setup
app = tk.Tk()
app.title("轨迹文件处理器")
app.geometry("600x350")
app.resizable(True, True)

# 设置主题风格
app.configure(bg="#f0f0f0")
style = {"padx": 10, "pady": 5, "anchor": "w"}

# 标题
title_frame = tk.Frame(app, bg="#f0f0f0")
title_frame.pack(pady=10, fill=tk.X)
tk.Label(title_frame, text="轨迹文件分割处理器", font=("Arial", 14, "bold"), bg="#f0f0f0").pack()

# 输入文件夹选择
input_frame = tk.Frame(app, bg="#f0f0f0")
input_frame.pack(pady=5, padx=20, fill=tk.X)

tk.Label(input_frame, text="选择文件夹:", font=("Arial", 10), bg="#f0f0f0", **style).pack(side=tk.LEFT)
input_folder_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
input_folder_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
tk.Button(input_frame, text="浏览", command=browse_input_folder, font=("Arial", 10), width=8).pack(side=tk.LEFT, padx=5)

# 帧范围设置
frame_range_frame = tk.Frame(app, bg="#f0f0f0")
frame_range_frame.pack(pady=10, padx=20, fill=tk.X)

tk.Label(frame_range_frame, text="分析帧数范围:", font=("Arial", 10), bg="#f0f0f0", **style).pack(side=tk.LEFT)
frame_range_entry = tk.Entry(frame_range_frame, width=15, font=("Arial", 10))
frame_range_entry.insert(0, "1-10")
frame_range_entry.pack(side=tk.LEFT, padx=5)

tk.Label(frame_range_frame, text="(格式: m-n, 例如: 1-10)", font=("Arial", 9), fg="gray", bg="#f0f0f0").pack(
    side=tk.LEFT, padx=5)

# 说明信息
instructions_frame = tk.Frame(app, bg="#f0f0f0")
instructions_frame.pack(pady=10, padx=20, fill=tk.X)

instructions = tk.Label(instructions_frame,
                        text="程序将递归处理选定文件夹及其所有子目录中的.lammpstrj文件\n"
                             "输出将保存到选定文件夹下的'reaction_mechanism'目录中\n"
                             "每个时间步文件夹包含连续两个时间步(TIMESTEP)的数据\n"
                             "排除文件夹: species_analysis, reaction_mechanism",
                        font=("Arial", 9),
                        justify=tk.LEFT,
                        bg="#f0f0f0")
instructions.pack(anchor="w")

# 按钮区域
button_frame = tk.Frame(app, bg="#f0f0f0")
button_frame.pack(pady=20)

process_button = tk.Button(button_frame, text="开始分析", command=process_files,
                           bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                           width=15, height=2)
process_button.pack()

# 状态栏
status_frame = tk.Frame(app, bd=1, relief=tk.SUNKEN, bg="#e0e0e0")
status_frame.pack(fill=tk.X, side=tk.BOTTOM)
status_label = tk.Label(status_frame, text="就绪 - 请选择文件夹", anchor=tk.W, bg="#e0e0e0")
status_label.pack(fill=tk.X, padx=5)

# 导入ttk用于进度条
from tkinter import ttk

app.mainloop()