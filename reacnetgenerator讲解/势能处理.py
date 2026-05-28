import pandas as pd
import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from threading import Thread


class LammpsEnergyExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("LAMMPS 能量数据整合工具")
        self.root.geometry("700x500")

        # 界面布局
        tk.Label(root, text="选择 log 文件所在文件夹:", font=('Arial', 10, 'bold')).pack(pady=(15, 0))
        path_frame = tk.Frame(root)
        path_frame.pack(pady=5, padx=20, fill='x')

        self.entry_path = tk.Entry(path_frame)
        self.entry_path.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry_path.insert(0, os.getcwd())

        tk.Button(path_frame, text="浏览", command=self.browse_folder).pack(side='right')

        self.btn_run = tk.Button(root, text="提取并生成对比表单", bg="#2196F3", fg="white",
                                 font=('Arial', 10, 'bold'), height=2, command=self.start_task)
        self.btn_run.pack(pady=15, padx=20, fill='x')

        self.log_area = scrolledtext.ScrolledText(root, height=18, state='disabled', bg="#f0f0f0")
        self.log_area.pack(pady=10, padx=20, fill='both', expand=True)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, folder)

    def write_log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_task(self):
        Thread(target=self.process_energy_data).start()

    def process_energy_data(self):
        target_dir = self.entry_path.get()
        if not os.path.isdir(target_dir):
            messagebox.showerror("错误", "路径不存在！")
            return

        os.chdir(target_dir)
        log_files = sorted(glob.glob("log.*"))
        if not log_files:
            self.write_log("❌ 未找到 log.* 文件")
            return

        self.btn_run.config(state='disabled')

        # 用于存储整合数据的字典
        # 结构: { 'PotEng': { 'filename1': Series, 'filename2': Series }, ... }
        summary_data = {
            'PotEng': {},
            'KinEng': {},
            'TotEng': {}
        }

        # 记录最长的 Step 序列作为基准列
        all_steps = None

        for file_path in log_files:
            fname = os.path.basename(file_path)
            self.write_log(f"读取文件: {fname}...")

            data = []
            headers = None
            is_collecting = False

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        parts = line.split()
                        if "Step" in parts and "PotEng" in parts:
                            headers = parts
                            is_collecting = True
                            continue
                        if "Loop time of" in line:
                            is_collecting = False
                            continue
                        if is_collecting and parts and parts[0].lstrip('-').isdigit():
                            data.append(parts)

                if data and headers:
                    df_temp = pd.DataFrame(data, columns=headers)
                    df_temp = df_temp.apply(pd.to_numeric, errors='coerce')

                    # 提取需要的列并存入字典，以文件名为列名
                    for target in ['PotEng', 'KinEng', 'TotEng']:
                        if target in df_temp.columns:
                            # 使用 Step 作为索引以便后续合并
                            summary_data[target][fname] = df_temp.set_index('Step')[target]

                    self.write_log(f"  ✅ 提取成功")
                else:
                    self.write_log(f"  ⚠️ 未发现数据块")
            except Exception as e:
                self.write_log(f"  ❌ 出错: {e}")

        # 导出到 Excel
        output_file = "Energy_Summary.xlsx"
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for key in summary_data:
                    if summary_data[key]:
                        # 将该类型的所有文件数据按 Step 合并
                        final_df = pd.DataFrame(summary_data[key])
                        # 将 Step 从索引变回第一列
                        final_df.reset_index(inplace=True)
                        final_df.to_excel(writer, sheet_name=key, index=False)
                        self.write_log(f"📊 已生成表单: {key}")

            self.write_log(f"\n✨ 全部完成！文件已存至: \n{output_file}")
            messagebox.showinfo("成功", f"整合数据已保存至 {output_file}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法生成Excel: {e}")
        finally:
            self.btn_run.config(state='normal')


if __name__ == "__main__":
    root = tk.Tk()
    app = LammpsEnergyExtractor(root)
    root.mainloop()