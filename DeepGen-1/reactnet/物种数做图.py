import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib

matplotlib.use('TkAgg')
from matplotlib import rcParams
import os

# 设置期刊要求的绘图样式
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 12
rcParams['axes.linewidth'] = 1.5
rcParams['lines.linewidth'] = 2
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['xtick.major.size'] = 8
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.size'] = 8
rcParams['ytick.major.width'] = 1.5
rcParams['legend.frameon'] = False
rcParams['legend.fontsize'] = 11


class SpeciesPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("物种数统计绘图工具")
        self.root.geometry("1000x700")

        # 创建框架
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.plot_frame = ttk.Frame(root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建控件
        ttk.Label(self.control_frame, text="物种数绘图工具", font=("Times New Roman", 14, "bold")).grid(row=0, column=0,
                                                                                                        pady=10)

        ttk.Button(self.control_frame, text="打开文件", command=self.open_file).grid(row=1, column=0, pady=5,
                                                                                     sticky=tk.W + tk.E)
        ttk.Button(self.control_frame, text="绘制图表", command=self.plot_data).grid(row=2, column=0, pady=5,
                                                                                     sticky=tk.W + tk.E)
        ttk.Button(self.control_frame, text="保存图表", command=self.save_plot).grid(row=3, column=0, pady=5,
                                                                                     sticky=tk.W + tk.E)

        # 图例位置选择
        ttk.Label(self.control_frame, text="图例位置:").grid(row=4, column=0, pady=(20, 5), sticky=tk.W)
        self.legend_pos = tk.StringVar(value="best")
        positions = [("自动", "best"), ("右上", "upper right"), ("左上", "upper left"),
                     ("右下", "lower right"), ("左下", "lower left"), ("右中", "right")]
        for i, (text, pos) in enumerate(positions):
            ttk.Radiobutton(self.control_frame, text=text, variable=self.legend_pos,
                            value=pos).grid(row=5 + i, column=0, sticky=tk.W)

        # 线条样式选项
        ttk.Label(self.control_frame, text="线条样式:").grid(row=11, column=0, pady=(20, 5), sticky=tk.W)
        self.line_style = tk.StringVar(value="-")
        styles = [("实线", "-"), ("虚线", "--"), ("点线", ":"), ("点划线", "-.")]
        for i, (text, style) in enumerate(styles):
            ttk.Radiobutton(self.control_frame, text=text, variable=self.line_style,
                            value=style).grid(row=12 + i, column=0, sticky=tk.W)

        # 添加颜色选择功能
        ttk.Label(self.control_frame, text="颜色方案:").grid(row=16, column=0, pady=(20, 5), sticky=tk.W)
        self.color_scheme = tk.StringVar(value="default")
        schemes = [("默认", "default"), ("期刊1", "tab10"), ("期刊2", "Set2"), ("期刊3", "Dark2")]
        for i, (text, scheme) in enumerate(schemes):
            ttk.Radiobutton(self.control_frame, text=text, variable=self.color_scheme,
                            value=scheme).grid(row=17 + i, column=0, sticky=tk.W)

        # 状态栏
        self.status = tk.StringVar(value="准备就绪")
        ttk.Label(self.control_frame, textvariable=self.status).grid(row=22, column=0, pady=20, sticky=tk.W)

        # 文件路径显示
        self.file_path_var = tk.StringVar(value="当前文件: 无")
        ttk.Label(self.control_frame, textvariable=self.file_path_var).grid(row=23, column=0, pady=5, sticky=tk.W)

        # 绘图区域
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始化数据
        self.df = None
        self.default_file = "物种数和分子数统计.xlsx"

        # 尝试加载默认文件
        if os.path.exists(self.default_file):
            self.file_path = self.default_file
            self.load_file()
        else:
            self.file_path = None
            self.file_path_var.set("当前文件: 无")
            self.status.set("请打开文件")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self.load_file()

    def load_file(self):
        try:
            # 尝试读取Excel文件
            self.df = pd.read_excel(self.file_path, sheet_name="物种数")

            # 更新状态和文件路径显示
            filename = os.path.basename(self.file_path)
            self.file_path_var.set(f"当前文件: {filename}")
            self.status.set(f"成功加载文件: {filename}")

            # 尝试自动绘制
            self.plot_data()
        except Exception as e:
            error_msg = f"加载文件错误: {str(e)}"
            self.status.set(error_msg)
            messagebox.showerror("文件错误", error_msg)

    def plot_data(self):
        if self.df is None:
            self.status.set("错误: 未加载数据")
            messagebox.showwarning("数据错误", "请先打开数据文件")
            return

        try:
            self.ax.clear()

            # 获取列名
            time_col = self.df.columns[0]
            species_cols = self.df.columns[1:]

            # 获取颜色方案
            color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
            if self.color_scheme.get() != "default":
                try:
                    color_cycle = plt.get_cmap(self.color_scheme.get()).colors
                except:
                    pass

            # 绘制折线图
            for i, col in enumerate(species_cols):
                color_idx = i % len(color_cycle)
                self.ax.plot(
                    self.df[time_col],
                    self.df[col],
                    linestyle=self.line_style.get(),
                    color=color_cycle[color_idx],
                    label=col
                )

            # 设置标签和标题
            self.ax.set_xlabel(time_col, fontsize=14, fontname='Times New Roman')
            self.ax.set_ylabel("物种数 (n)", fontsize=14, fontname='Times New Roman')
            self.ax.set_title("物种数随时间变化", fontsize=16, fontname='Times New Roman', pad=20)

            # 添加图例
            self.ax.legend(loc=self.legend_pos.get(), fontsize=11)

            # 设置网格
            self.ax.grid(True, linestyle='--', alpha=0.7)

            # 格式化坐标轴
            self.ax.tick_params(axis='both', which='major', labelsize=12)

            # 优化布局
            self.fig.tight_layout()

            self.canvas.draw()
            self.status.set("图表绘制成功")
        except Exception as e:
            error_msg = f"绘图错误: {str(e)}"
            self.status.set(error_msg)
            messagebox.showerror("绘图错误", error_msg)

    def save_plot(self):
        if self.fig:
            file_types = [
                ('PDF 文件', '*.pdf'),
                ('EPS 文件', '*.eps'),
                ('PNG 文件', '*.png'),
                ('TIFF 文件', '*.tiff'),
                ('SVG 文件', '*.svg')
            ]
            file_path = filedialog.asksaveasfilename(
                filetypes=file_types,
                defaultextension=".pdf",
                title="保存图表"
            )
            if file_path:
                try:
                    format = file_path.split('.')[-1].lower()
                    if format == 'tiff':
                        format = 'tif'

                    self.fig.savefig(
                        file_path,
                        dpi=600,
                        bbox_inches='tight',
                        format=format
                    )
                    self.status.set(f"图表已保存至: {file_path}")
                    messagebox.showinfo("保存成功", f"图表已成功保存为:\n{file_path}")
                except Exception as e:
                    error_msg = f"保存失败: {str(e)}"
                    self.status.set(error_msg)
                    messagebox.showerror("保存错误", error_msg)
        else:
            messagebox.showwarning("保存错误", "没有可保存的图表")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeciesPlotter(root)
    root.mainloop()