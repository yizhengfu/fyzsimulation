import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from joblib import load
import os
import sys
from pathlib import Path


class MLModelPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("机器学习模型预测工具")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # 变量
        self.model_file_var = tk.StringVar()
        self.scaler_file_var = tk.StringVar()
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.has_scaler_var = tk.BooleanVar(value=False)
        self.target_column_var = tk.StringVar(value="Formula")  # 默认为Formula，可更改
        self.status_var = tk.StringVar(value="就绪")

        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 样式
        style = ttk.Style()
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TButton", font=("Microsoft YaHei", 10))
        style.configure("TCheckbutton", font=("Microsoft YaHei", 10))

        # 1. 模型文件选择
        model_frame = ttk.LabelFrame(main_frame, text="步骤1: 选择模型文件", padding="10")
        model_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(model_frame, text="模型文件(.joblib):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.model_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(model_frame, text="浏览...", command=self.browse_model_file).grid(row=0, column=2, padx=5, pady=5)

        # 2. 标准化器选择（可选）
        scaler_frame = ttk.Frame(main_frame)
        scaler_frame.pack(fill=tk.X, padx=5, pady=0)

        ttk.Checkbutton(scaler_frame, text="使用数据标准化器", variable=self.has_scaler_var,
                        command=self.toggle_scaler).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.scaler_subframe = ttk.Frame(scaler_frame)
        self.scaler_subframe.grid(row=1, column=0, columnspan=3, sticky=tk.W + tk.E, padx=5, pady=0)
        self.scaler_subframe.grid_remove()  # 默认隐藏

        ttk.Label(self.scaler_subframe, text="标准化器文件(.joblib):").grid(row=0, column=0, sticky=tk.W, padx=5,
                                                                            pady=5)
        ttk.Entry(self.scaler_subframe, textvariable=self.scaler_file_var, width=47).grid(row=0, column=1, padx=5,
                                                                                          pady=5)
        ttk.Button(self.scaler_subframe, text="浏览...", command=self.browse_scaler_file).grid(row=0, column=2, padx=5,
                                                                                               pady=5)

        # 3. 数据文件选择
        data_frame = ttk.LabelFrame(main_frame, text="步骤2: 选择预测数据文件", padding="10")
        data_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(data_frame, text="CSV数据文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(data_frame, textvariable=self.input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(data_frame, text="浏览...", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

        # 4. 目标列设置
        target_frame = ttk.Frame(data_frame)
        target_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(target_frame, text="目标/ID列名称:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(target_frame, textvariable=self.target_column_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(target_frame, text="(留空则不使用ID列)").pack(side=tk.LEFT, padx=5)

        # 5. 输出文件选择
        output_frame = ttk.LabelFrame(main_frame, text="步骤3: 选择输出文件", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="输出CSV文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="浏览...", command=self.browse_output_file).grid(row=0, column=2, padx=5, pady=5)

        # 6. 执行按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=15)

        ttk.Button(button_frame, text="开始预测", command=self.run_prediction, width=20).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear_fields, width=10).pack(side=tk.RIGHT, padx=5)

        # 7. 状态栏和日志
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        log_frame = ttk.LabelFrame(main_frame, text="日志信息")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=8, width=80, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def toggle_scaler(self):
        if self.has_scaler_var.get():
            self.scaler_subframe.grid()
        else:
            self.scaler_subframe.grid_remove()

    def browse_model_file(self):
        filetypes = [("Joblib文件", "*.joblib"), ("所有文件", "*.*")]
        filename = filedialog.askopenfilename(title="选择模型文件", filetypes=filetypes)
        if filename:
            self.model_file_var.set(filename)
            self.log("已选择模型文件: " + filename)

            # 自动设置默认输出文件名
            if not self.output_file_var.get():
                base_dir = os.path.dirname(filename)
                out_filename = os.path.join(base_dir, "prediction_results.csv")
                self.output_file_var.set(out_filename)

    def browse_scaler_file(self):
        filetypes = [("Joblib文件", "*.joblib"), ("所有文件", "*.*")]
        filename = filedialog.askopenfilename(title="选择标准化器文件", filetypes=filetypes)
        if filename:
            self.scaler_file_var.set(filename)
            self.log("已选择标准化器文件: " + filename)

    def browse_input_file(self):
        filetypes = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
        filename = filedialog.askopenfilename(title="选择预测数据文件", filetypes=filetypes)
        if filename:
            self.input_file_var.set(filename)
            self.log("已选择数据文件: " + filename)

            # 尝试读取并显示数据列名
            try:
                df = pd.read_csv(filename, nrows=0)  # 只读取标题行
                columns = df.columns.tolist()
                self.log(f"数据文件的列名: {', '.join(columns)}")

                # 自动识别可能的ID列
                possible_id_columns = [col for col in columns if
                                       any(id_term in col.lower() for id_term in ['id', 'name', 'formula', 'compound'])]
                if possible_id_columns and not self.target_column_var.get():
                    self.target_column_var.set(possible_id_columns[0])
                    self.log(f"自动识别ID列: {possible_id_columns[0]}")
            except Exception as e:
                self.log(f"读取数据文件列名时出错: {str(e)}")

    def browse_output_file(self):
        filetypes = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
        filename = filedialog.asksaveasfilename(title="保存预测结果", filetypes=filetypes,
                                                defaultextension=".csv")
        if filename:
            self.output_file_var.set(filename)
            self.log("已设置输出文件: " + filename)

    def clear_fields(self):
        self.model_file_var.set("")
        self.scaler_file_var.set("")
        self.input_file_var.set("")
        self.output_file_var.set("")
        self.target_column_var.set("Formula")
        self.has_scaler_var.set(False)
        self.toggle_scaler()
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("就绪")
        self.log("已清除所有字段")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最新的日志

    def validate_inputs(self):
        model_file = self.model_file_var.get().strip()
        input_file = self.input_file_var.get().strip()
        output_file = self.output_file_var.get().strip()

        if not model_file:
            messagebox.showerror("错误", "请选择模型文件")
            return False

        if not os.path.exists(model_file):
            messagebox.showerror("错误", f"模型文件不存在: {model_file}")
            return False

        # 检查标准化器文件（如果启用）
        if self.has_scaler_var.get():
            scaler_file = self.scaler_file_var.get().strip()
            if not scaler_file:
                messagebox.showerror("错误", "已启用标准化器选项，请选择标准化器文件")
                return False

            if not os.path.exists(scaler_file):
                messagebox.showerror("错误", f"标准化器文件不存在: {scaler_file}")
                return False

        if not input_file:
            messagebox.showerror("错误", "请选择输入CSV数据文件")
            return False

        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件不存在: {input_file}")
            return False

        if not output_file:
            messagebox.showerror("错误", "请选择输出文件路径")
            return False

        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.log(f"创建输出目录: {output_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录: {str(e)}")
                return False

        return True

    def run_prediction(self):
        if not self.validate_inputs():
            return

        self.status_var.set("预测中...")
        self.root.update_idletasks()

        try:
            model_file = self.model_file_var.get()
            input_file = self.input_file_var.get()
            output_file = self.output_file_var.get()
            target_column = self.target_column_var.get().strip()

            # 加载模型
            self.log("加载模型...")
            model = load(model_file)

            # 加载标准化器（如果有）
            scaler = None
            if self.has_scaler_var.get():
                scaler_file = self.scaler_file_var.get()
                self.log("加载标准化器...")
                scaler = load(scaler_file)

            # 加载数据
            self.log("加载预测数据...")
            new_data = pd.read_csv(input_file)

            # 处理目标/ID列
            has_target_col = False
            if target_column and target_column in new_data.columns:
                self.log(f"找到目标列: {target_column}")
                target_values = new_data[target_column].copy()
                X_new = new_data.drop([target_column], axis=1)
                has_target_col = True
            else:
                if target_column:
                    self.log(f"警告: 未找到指定的目标列 '{target_column}'，将使用所有列作为特征")
                X_new = new_data.copy()

            # 标准化数据（如果需要）
            if scaler is not None:
                self.log("标准化数据...")
                try:
                    X_new_processed = scaler.transform(X_new)
                except Exception as e:
                    self.log(f"警告: 标准化数据时出错，尝试使用原始数据: {str(e)}")
                    X_new_processed = X_new
            else:
                X_new_processed = X_new

            # 预测
            self.log("执行预测...")
            try:
                predictions = model.predict(X_new_processed)
                self.log(f"预测完成，得到 {len(predictions)} 个结果")
            except Exception as e:
                # 尝试直接使用原始数据
                if scaler is not None:
                    self.log(f"使用标准化数据预测失败: {str(e)}，尝试使用原始数据...")
                    try:
                        predictions = model.predict(X_new)
                        self.log("使用原始数据预测成功")
                    except Exception as e2:
                        raise Exception(f"预测失败: {str(e2)}")
                else:
                    raise e

            # 创建结果DataFrame
            if has_target_col:
                result_df = pd.DataFrame({
                    target_column: target_values,
                    'Predicted_Value': predictions
                })
            else:
                result_df = pd.DataFrame({
                    'Predicted_Value': predictions
                })

            # 保存结果
            result_df.to_csv(output_file, index=False)

            self.log(f"预测完成! 结果已保存到: {output_file}")
            self.status_var.set("预测完成")

            # 询问是否打开结果文件
            if messagebox.askyesno("完成", f"预测已完成，结果保存在:\n{output_file}\n\n是否打开结果文件?"):
                self.open_file(output_file)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            self.status_var.set("出错")
            messagebox.showerror("预测错误", f"预测过程中出错:\n{str(e)}")

    def open_file(self, filepath):
        """尝试用系统默认程序打开文件"""
        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{filepath}"')
            else:  # Linux
                os.system(f'xdg-open "{filepath}"')
        except Exception as e:
            self.log(f"无法打开文件: {str(e)}")
            messagebox.showwarning("警告", f"无法打开结果文件: {str(e)}")


def main():
    root = tk.Tk()
    app = MLModelPredictorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()