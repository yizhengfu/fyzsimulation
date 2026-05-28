import os
import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser, simpledialog, StringVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import sys
import matplotlib
from matplotlib.font_manager import FontProperties
import platform
import json

# 设置matplotlib使用TkAgg后端
matplotlib.use('TkAgg')


# 解决中文显示问题
def set_chinese_font():
    """设置支持中文的字体"""
    system_name = platform.system()
    if system_name == 'Windows':
        plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统使用黑体
    elif system_name == 'Darwin':
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统使用Arial Unicode MS
    else:
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # Linux系统使用文泉驿正黑

    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['font.weight'] = 'bold'  # 默认所有字体加粗


# 在程序启动时设置中文字体
set_chinese_font()

# 设置文件路径
SETTINGS_FILE = "plot_settings.json"


class PlotSettingsDialog(simpledialog.Dialog):
    """自定义绘图设置对话框"""

    def __init__(self, parent, title, initial_settings=None):
        self.initial_settings = initial_settings or {}
        super().__init__(parent, title)

    def body(self, master):
        # 创建选项卡
        notebook = ttk.Notebook(master)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 第一页：基本设置
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text='基本设置')

        # 第二页：文本设置
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text='文本设置')

        # 第三页：高级设置
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text='高级设置')

        # 基本设置页内容
        tk.Label(basic_frame, text="散点大小:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.scatter_size = tk.Scale(basic_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.scatter_size.set(self.initial_settings.get('scatter_size', 20))
        self.scatter_size.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(basic_frame, text="散点颜色:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.scatter_color_btn = tk.Button(basic_frame, text="选择颜色",
                                           command=lambda: self.choose_color('scatter_color'))
        self.scatter_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.scatter_color = self.initial_settings.get('scatter_color', 'blue')
        self.scatter_color_btn.config(bg=self.scatter_color)

        tk.Label(basic_frame, text="线条颜色:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.line_color_btn = tk.Button(basic_frame, text="选择颜色",
                                        command=lambda: self.choose_color('line_color'))
        self.line_color_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.line_color = self.initial_settings.get('line_color', 'red')
        self.line_color_btn.config(bg=self.line_color)

        tk.Label(basic_frame, text="线条粗细:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.line_width = tk.Scale(basic_frame, from_=0.5, to=5, resolution=0.1, orient=tk.HORIZONTAL)
        self.line_width.set(self.initial_settings.get('line_width', 2.0))
        self.line_width.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # 文本设置页内容
        tk.Label(text_frame, text="图例名称:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.scatter_label = tk.Entry(text_frame, width=30)
        self.scatter_label.insert(0, self.initial_settings.get('scatter_label', '数据点'))
        self.scatter_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(text_frame, text="直线名称:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.line_label = tk.Entry(text_frame, width=30)
        self.line_label.insert(0, self.initial_settings.get('line_label', 'X=Y'))
        self.line_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(text_frame, text="图表标题:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.plot_title = tk.Entry(text_frame, width=30)
        self.plot_title.insert(0, self.initial_settings.get('plot_title', ''))
        self.plot_title.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(text_frame, text="R值前缀:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.r_prefix = tk.Entry(text_frame, width=30)
        self.r_prefix.insert(0, self.initial_settings.get('r_prefix', 'R = '))
        self.r_prefix.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(text_frame, text="RMSE前缀:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.rmse_prefix = tk.Entry(text_frame, width=30)
        self.rmse_prefix.insert(0, self.initial_settings.get('rmse_prefix', 'RMSE = '))
        self.rmse_prefix.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # 高级设置页内容
        tk.Label(advanced_frame, text="小数位数:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.decimal_places = tk.Scale(advanced_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.decimal_places.set(self.initial_settings.get('decimal_places', 3))
        self.decimal_places.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 字体设置
        tk.Label(advanced_frame, text="轴标题字体:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.axis_font_family = ttk.Combobox(advanced_frame,
                                             values=["sans-serif", "serif", "monospace", "Arial", "Times New Roman",
                                                     "Courier New"])
        self.axis_font_family.set(self.initial_settings.get('axis_font_family', 'sans-serif'))
        self.axis_font_family.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(advanced_frame, text="轴标题字号:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.axis_font_size = tk.Scale(advanced_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.axis_font_size.set(self.initial_settings.get('axis_font_size', 12))
        self.axis_font_size.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(advanced_frame, text="刻度字体:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tick_font_family = ttk.Combobox(advanced_frame,
                                             values=["sans-serif", "serif", "monospace", "Arial", "Times New Roman",
                                                     "Courier New"])
        self.tick_font_family.set(self.initial_settings.get('tick_font_family', 'sans-serif'))
        self.tick_font_family.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(advanced_frame, text="刻度字号:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.tick_font_size = tk.Scale(advanced_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.tick_font_size.set(self.initial_settings.get('tick_font_size', 10))
        self.tick_font_size.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # 坐标轴线宽
        tk.Label(advanced_frame, text="坐标轴线宽:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.axis_line_width = tk.Scale(advanced_frame, from_=0.1, to=5, resolution=0.1, orient=tk.HORIZONTAL)
        self.axis_line_width.set(self.initial_settings.get('axis_line_width', 1.0))
        self.axis_line_width.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # 显示选项
        self.show_r_var = tk.BooleanVar(value=self.initial_settings.get('show_r', True))
        tk.Checkbutton(advanced_frame, text="显示R值", variable=self.show_r_var).grid(row=4, column=0, sticky="w",
                                                                                      padx=5, pady=5)

        self.show_rmse_var = tk.BooleanVar(value=self.initial_settings.get('show_rmse', True))
        tk.Checkbutton(advanced_frame, text="显示RMSE值", variable=self.show_rmse_var).grid(row=4, column=1, sticky="w",
                                                                                            padx=5, pady=5)

        self.show_title_var = tk.BooleanVar(value=self.initial_settings.get('show_title', True))
        tk.Checkbutton(advanced_frame, text="显示图表标题", variable=self.show_title_var).grid(row=4, column=2,
                                                                                               sticky="w", padx=5,
                                                                                               pady=5)

        self.show_legend_var = tk.BooleanVar(value=self.initial_settings.get('show_legend', True))
        tk.Checkbutton(advanced_frame, text="显示图例", variable=self.show_legend_var).grid(row=4, column=3, sticky="w",
                                                                                            padx=5, pady=5)

        # 字体加粗选项
        self.bold_axis_var = tk.BooleanVar(value=self.initial_settings.get('bold_axis', True))
        tk.Checkbutton(advanced_frame, text="轴标题加粗", variable=self.bold_axis_var).grid(row=5, column=0, sticky="w",
                                                                                            padx=5, pady=5)

        self.bold_tick_var = tk.BooleanVar(value=self.initial_settings.get('bold_tick', True))
        tk.Checkbutton(advanced_frame, text="刻度加粗", variable=self.bold_tick_var).grid(row=5, column=1, sticky="w",
                                                                                          padx=5, pady=5)

        self.bold_legend_var = tk.BooleanVar(value=self.initial_settings.get('bold_legend', True))
        tk.Checkbutton(advanced_frame, text="图例加粗", variable=self.bold_legend_var).grid(row=5, column=2, sticky="w",
                                                                                            padx=5, pady=5)

        self.bold_text_var = tk.BooleanVar(value=self.initial_settings.get('bold_text', True))
        tk.Checkbutton(advanced_frame, text="文本加粗", variable=self.bold_text_var).grid(row=5, column=3, sticky="w",
                                                                                          padx=5, pady=5)

        # 配置列权重
        for frame in [basic_frame, text_frame, advanced_frame]:
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(3, weight=1)

        return self.scatter_label  # 初始焦点

    def choose_color(self, color_type):
        """打开颜色选择对话框"""
        color = colorchooser.askcolor()[1]
        if color:
            if color_type == 'scatter_color':
                self.scatter_color = color
                self.scatter_color_btn.config(bg=color)
            else:
                self.line_color = color
                self.line_color_btn.config(bg=color)

    def apply(self):
        """应用设置"""
        self.result = {
            'scatter_size': self.scatter_size.get(),
            'scatter_color': self.scatter_color,
            'line_color': self.line_color,
            'line_width': self.line_width.get(),
            'scatter_label': self.scatter_label.get(),
            'line_label': self.line_label.get(),
            'plot_title': self.plot_title.get(),
            'r_prefix': self.r_prefix.get(),
            'rmse_prefix': self.rmse_prefix.get(),
            'decimal_places': self.decimal_places.get(),
            'axis_font_family': self.axis_font_family.get(),
            'axis_font_size': self.axis_font_size.get(),
            'tick_font_family': self.tick_font_family.get(),
            'tick_font_size': self.tick_font_size.get(),
            'axis_line_width': self.axis_line_width.get(),
            'show_r': self.show_r_var.get(),
            'show_rmse': self.show_rmse_var.get(),
            'show_title': self.show_title_var.get(),
            'show_legend': self.show_legend_var.get(),
            'bold_axis': self.bold_axis_var.get(),
            'bold_tick': self.bold_tick_var.get(),
            'bold_legend': self.bold_legend_var.get(),
            'bold_text': self.bold_text_var.get()
        }


def process_out_file(file_path):
    """处理.out文件，根据列数创建不同格式的Excel文件"""
    try:
        # 读取文件内容
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # 准备存储数据的列表
        data = []

        # 处理每一行数据
        for line in lines:
            # 跳过空行和注释行
            if not line.strip() or line.strip().startswith('#'):
                continue

            # 使用正则表达式分割数据（处理多个空格和制表符）
            parts = re.split(r'[\s\t]+', line.strip())

            # 确保有足够的数据列
            if len(parts) < 2:
                continue

            try:
                # 保留完整数据，不进行四舍五入
                row_data = [float(x) for x in parts]
                data.append(row_data)
            except ValueError:
                # 如果转换失败，跳过该行
                print(f"跳过无法解析的行: {line.strip()}")

        # 检查数据是否为空
        if not data:
            raise ValueError("文件中没有有效数据")

        # 确定列数
        num_cols = len(data[0])

        # 根据列数创建不同格式的DataFrame
        if num_cols == 2:
            # 能量数据
            df = pd.DataFrame(data, columns=[
                'Energy of DFT',
                'Energy predicted by deep potential'
            ])
        elif num_cols == 6:
            # 力分量数据
            df = pd.DataFrame(data, columns=[
                'Force(X) of DFT',
                'Force(Y) of DFT',
                'Force(Z) of DFT',
                'Force(X) predicted by deep potential',
                'Force(Y) predicted by deep potential',
                'Force(Z) predicted by deep potential'
            ])
        elif num_cols == 18:
            # 维里张量数据
            df = pd.DataFrame(data, columns=[
                'Virial(XX) of DFT',
                'Virial(XY) of DFT',
                'Virial(XZ) of DFT',
                'Virial(YX) of DFT',
                'Virial(YY) of DFT',
                'Virial(YZ) of DFT',
                'Virial(ZX) of DFT',
                'Virial(ZY) of DFT',
                'Virial(ZZ) of DFT',
                'Virial(XX) predicted by deep potential',
                'Virial(XY) predicted by deep potential',
                'Virial(XZ) predicted by deep potential',
                'Virial(YX) predicted by deep potential',
                'Virial(YY) predicted by deep potential',
                'Virial(YZ) predicted by deep potential',
                'Virial(ZX) predicted by deep potential',
                'Virial(ZY) predicted by deep potential',
                'Virial(ZZ) predicted by deep potential'
            ])
        else:
            # 不支持其他列数
            raise ValueError(f"不支持{num_cols}列的数据格式，支持2列、6列或18列")

        # 创建输出文件名（相同名称，扩展名改为.xlsx）
        output_file = os.path.splitext(file_path)[0] + '.xlsx'

        # 保存为Excel文件
        df.to_excel(output_file, index=False)
        return output_file, num_cols, df  # 返回DataFrame用于绘图

    except Exception as e:
        # 捕获并重新抛出异常，以便在GUI中显示
        raise RuntimeError(f"处理文件时出错: {str(e)}") from e


def plot_energy_data(df, excel_file, output_dir, settings):
    """绘制能量数据的散点图"""
    # 确保有两列数据
    if len(df.columns) < 2:
        raise ValueError("能量数据必须包含至少两列")

    # 提取数据
    x = df.iloc[:, 0]  # 第一列
    y = df.iloc[:, 1]  # 第二列

    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 8))  # 正方形图形

    # 应用用户设置
    scatter_size = settings.get('scatter_size', 20)
    scatter_color = settings.get('scatter_color', 'blue')
    line_color = settings.get('line_color', 'red')
    line_width = settings.get('line_width', 2.0)
    scatter_label = settings.get('scatter_label', '数据点')
    line_label = settings.get('line_label', 'X=Y')
    plot_title = settings.get('plot_title', '')
    r_prefix = settings.get('r_prefix', 'R = ')
    rmse_prefix = settings.get('rmse_prefix', 'RMSE = ')
    decimal_places = settings.get('decimal_places', 3)
    axis_font_family = settings.get('axis_font_family', 'sans-serif')
    axis_font_size = settings.get('axis_font_size', 12)
    tick_font_family = settings.get('tick_font_family', 'sans-serif')
    tick_font_size = settings.get('tick_font_size', 10)
    axis_line_width = settings.get('axis_line_width', 1.0)
    show_r = settings.get('show_r', True)
    show_rmse = settings.get('show_rmse', True)
    show_title = settings.get('show_title', True)
    show_legend = settings.get('show_legend', True)

    # 字体加粗设置
    bold_axis = 'bold' if settings.get('bold_axis', True) else 'normal'
    bold_tick = 'bold' if settings.get('bold_tick', True) else 'normal'
    bold_legend = 'bold' if settings.get('bold_legend', True) else 'normal'
    bold_text = 'bold' if settings.get('bold_text', True) else 'normal'

    # 设置轴标题字体
    axis_font = {'family': axis_font_family, 'size': axis_font_size, 'weight': bold_axis}

    # 设置刻度字体
    tick_font = {'family': tick_font_family, 'size': tick_font_size, 'weight': bold_tick}

    # 如果没有提供标题，使用默认标题
    if not plot_title:
        filename = os.path.basename(excel_file)
        plot_title = f'DFT vs Deep Potential Energy: {filename}'

    # 绘制散点图
    ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)

    # 计算数据范围
    min_val = min(x.min(), y.min())
    max_val = max(x.max(), y.max())

    # 扩展范围（增加10%的边距）
    margin = 0.1 * (max_val - min_val)
    plot_min = min_val - margin
    plot_max = max_val + margin

    # 绘制X=Y直线
    line_x = np.linspace(plot_min, plot_max, 100)
    ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)

    # 设置坐标轴标签（添加单位）
    ax.set_xlabel('Energy of DFT (eV/atom)', fontdict=axis_font)
    ax.set_ylabel('Energy predicted by deep potential (eV/atom)', fontdict=axis_font)

    # 设置标题（如果用户选择显示）
    if show_title:
        ax.set_title(plot_title, fontsize=14, weight=bold_axis)

    # 设置坐标轴范围
    ax.set_xlim([plot_min, plot_max])
    ax.set_ylim([plot_min, plot_max])

    # 设置坐标轴比例相等
    ax.set_aspect('equal', adjustable='box')

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 设置刻度字体
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontfamily(tick_font_family)
        label.set_fontsize(tick_font_size)
        label.set_fontweight(bold_tick)

    # 设置坐标轴线宽
    for spine in ax.spines.values():
        spine.set_linewidth(axis_line_width)

    # 添加图例（如果用户选择显示）
    if show_legend:
        legend = ax.legend()
        for text in legend.get_texts():
            text.set_fontweight(bold_legend)

    # 初始化文本字符串
    text_str = ""

    # 添加文本显示相关系数（如果用户选择显示）
    if show_r or show_rmse:
        r_value = np.corrcoef(x, y)[0, 1]
        rmse = np.sqrt(np.mean((x - y) ** 2))

        # 格式化R和RMSE值，根据用户设置的小数位数
        fmt_str = f".{decimal_places}f"
        text_str = ""

        if show_r:
            r_value_str = format(r_value, fmt_str)
            text_str += f'{r_prefix}{r_value_str}\n'

        if show_rmse:
            rmse_str = format(rmse, fmt_str)
            text_str += f'{rmse_prefix}{rmse_str}'

        # 移除多余的换行符
        text_str = text_str.strip()

        if text_str:
            ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                    fontsize=12, verticalalignment='top', weight=bold_text,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 保存图像
    plot_file = os.path.join(output_dir, os.path.splitext(os.path.basename(excel_file))[0] + '_energy_plot.png')
    plt.tight_layout()

    # 设置DPI并保存
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close(fig)  # 关闭图形以释放内存

    # 重新打开图形以在GUI中预览
    fig, ax = plt.subplots(figsize=(8, 8))  # 正方形预览
    ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)
    ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)
    ax.set_xlabel('Energy of DFT (eV/atom)', fontdict=axis_font)
    ax.set_ylabel('Energy predicted by deep potential (eV/atom)', fontdict=axis_font)
    if show_title:
        ax.set_title(plot_title, fontsize=14, weight=bold_axis)
    ax.set_xlim([plot_min, plot_max])
    ax.set_ylim([plot_min, plot_max])
    ax.set_aspect('equal', adjustable='box')  # 设置等比例坐标轴
    ax.grid(True, linestyle='--', alpha=0.7)

    # 设置刻度字体
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontfamily(tick_font_family)
        label.set_fontsize(tick_font_size)
        label.set_fontweight(bold_tick)

    # 设置坐标轴线宽
    for spine in ax.spines.values():
        spine.set_linewidth(axis_line_width)

    if show_legend:
        legend = ax.legend()
        for text in legend.get_texts():
            text.set_fontweight(bold_legend)
    if text_str:  # 这里text_str已经初始化，不会出现未定义错误
        ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                fontsize=12, verticalalignment='top', weight=bold_text,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    return fig, [plot_file]


def plot_force_data(df, excel_file, output_dir, settings):
    """绘制力分量数据的散点图"""
    # 确保有六列数据
    if len(df.columns) < 6:
        raise ValueError("力分量数据必须包含六列")

    # 应用用户设置
    scatter_size = settings.get('scatter_size', 20)
    scatter_color = settings.get('scatter_color', 'blue')
    line_color = settings.get('line_color', 'red')
    line_width = settings.get('line_width', 2.0)
    scatter_label = settings.get('scatter_label', '数据点')
    line_label = settings.get('line_label', 'X=Y')
    plot_title = settings.get('plot_title', '')
    r_prefix = settings.get('r_prefix', 'R = ')
    rmse_prefix = settings.get('rmse_prefix', 'RMSE = ')
    decimal_places = settings.get('decimal_places', 3)
    axis_font_family = settings.get('axis_font_family', 'sans-serif')
    axis_font_size = settings.get('axis_font_size', 12)
    tick_font_family = settings.get('tick_font_family', 'sans-serif')
    tick_font_size = settings.get('tick_font_size', 10)
    axis_line_width = settings.get('axis_line_width', 1.0)
    show_r = settings.get('show_r', True)
    show_rmse = settings.get('show_rmse', True)
    show_title = settings.get('show_title', True)
    show_legend = settings.get('show_legend', True)

    # 字体加粗设置
    bold_axis = 'bold' if settings.get('bold_axis', True) else 'normal'
    bold_tick = 'bold' if settings.get('bold_tick', True) else 'normal'
    bold_legend = 'bold' if settings.get('bold_legend', True) else 'normal'
    bold_text = 'bold' if settings.get('bold_text', True) else 'normal'

    # 设置轴标题字体
    axis_font = {'family': axis_font_family, 'size': axis_font_size, 'weight': bold_axis}

    # 设置刻度字体
    tick_font = {'family': tick_font_family, 'size': tick_font_size, 'weight': bold_tick}

    # 如果没有提供标题，使用默认标题
    if not plot_title:
        filename = os.path.basename(excel_file)
        plot_title = f'DFT vs Deep Potential Force Components: {filename}'

    # 分量名称
    components = ['X', 'Y', 'Z']

    # 存储所有图像文件路径
    plot_files = []

    # 计算全局数据范围（所有力分量）
    global_min = float('inf')
    global_max = float('-inf')

    # 遍历所有分量找出全局最小值和最大值
    for i in range(3):
        # 提取DFT分量和对应的DP预测分量
        dft_col = i
        dp_col = i + 3
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 更新全局范围
        min_val = min(x.min(), y.min())
        max_val = max(x.max(), y.max())

        if min_val < global_min:
            global_min = min_val
        if max_val > global_max:
            global_max = max_val

    # 扩展范围（增加10%的边距）
    margin = 0.1 * (global_max - global_min)
    plot_min = global_min - margin
    plot_max = global_max + margin

    # 创建图形（三张子图）用于预览
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 设置总标题（如果用户选择显示）
    if show_title:
        fig.suptitle(plot_title, fontsize=16, weight=bold_axis)

    # 绘制每个分量的散点图
    for i, comp in enumerate(components):
        ax = axes[i]

        # 提取数据：DFT分量和对应的DP预测分量
        dft_col = i
        dp_col = i + 3
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 绘制散点图
        ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)

        # 绘制X=Y直线
        line_x = np.linspace(plot_min, plot_max, 100)
        ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)

        # 设置坐标轴标签（添加单位）
        ax.set_xlabel(f'Force({comp}) of DFT (eV/Å)', fontdict=axis_font)
        ax.set_ylabel(f'Force({comp}) predicted by deep potential (eV/Å)', fontdict=axis_font)

        # 设置标题
        ax.set_title(f'Force {comp} Component', fontsize=14, weight=bold_axis)

        # 设置坐标轴范围（使用全局范围）
        ax.set_xlim([plot_min, plot_max])
        ax.set_ylim([plot_min, plot_max])

        # 设置坐标轴比例相等
        ax.set_aspect('equal', adjustable='box')

        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax.spines.values():
            spine.set_linewidth(axis_line_width)

        # 添加图例（只在第一个子图添加）
        if i == 0 and show_legend:
            legend = ax.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)

        # 添加文本显示相关系数（如果用户选择显示）
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值，根据用户设置的小数位数
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

            if text_str:
                ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                        fontsize=10, verticalalignment='top', weight=bold_text,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为总标题留出空间

    # 保存组合图
    combined_file = os.path.join(output_dir, os.path.splitext(os.path.basename(excel_file))[0] + '_force_combined.png')
    plt.savefig(combined_file, dpi=300, bbox_inches='tight')
    plot_files.append(combined_file)
    plt.close(fig)  # 关闭图形以释放内存

    # 创建并保存单独的图像（正方形）
    for i, comp in enumerate(components):
        # 创建新图形（正方形）
        fig_single, ax_single = plt.subplots(figsize=(8, 8))

        # 提取数据
        dft_col = i
        dp_col = i + 3
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 绘制散点图
        ax_single.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)

        # 绘制X=Y直线
        ax_single.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)

        # 设置坐标轴标签（添加单位）
        ax_single.set_xlabel(f'Force({comp}) of DFT (eV/Å)', fontdict=axis_font)
        ax_single.set_ylabel(f'Force({comp}) predicted by deep potential (eV/Å)', fontdict=axis_font)

        # 设置标题
        filename = os.path.basename(excel_file)
        if show_title:
            if plot_title:
                ax_single.set_title(f'Force {comp} Component: {plot_title}', fontsize=14, weight=bold_axis)
            else:
                ax_single.set_title(f'Force {comp} Component: {filename}', fontsize=14, weight=bold_axis)

        # 设置坐标轴范围（使用全局范围）
        ax_single.set_xlim([plot_min, plot_max])
        ax_single.set_ylim([plot_min, plot_max])

        # 设置坐标轴比例相等
        ax_single.set_aspect('equal', adjustable='box')

        # 添加网格
        ax_single.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax_single.get_xticklabels() + ax_single.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax_single.spines.values():
            spine.set_linewidth(axis_line_width)

        # 添加图例
        if show_legend:
            legend = ax_single.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)

        # 添加文本显示相关系数（如果用户选择显示）
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值，根据用户设置的小数位数
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

            if text_str:
                ax_single.text(0.05, 0.95, text_str, transform=ax_single.transAxes,
                               fontsize=10, verticalalignment='top', weight=bold_text,
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 保存单独图像
        plot_file = os.path.join(output_dir, os.path.splitext(filename)[0] + f'_force_{comp}_plot.png')
        plt.tight_layout()
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plot_files.append(plot_file)
        plt.close(fig_single)

    # 重新打开图形以在GUI中预览
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    if show_title:
        fig.suptitle(plot_title, fontsize=16, weight=bold_axis)

    # 绘制每个分量的散点图（用于预览）
    for i, comp in enumerate(components):
        ax = axes[i]
        dft_col = i
        dp_col = i + 3
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 计算相关系数和RMSE
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

        ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)
        ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)
        ax.set_xlabel(f'Force({comp}) of DFT (eV/Å)', fontdict=axis_font)
        ax.set_ylabel(f'Force({comp}) predicted by deep potential (eV/Å)', fontdict=axis_font)
        ax.set_title(f'Force {comp} Component', fontsize=14, weight=bold_axis)
        ax.set_xlim([plot_min, plot_max])
        ax.set_ylim([plot_min, plot_max])
        ax.set_aspect('equal', adjustable='box')  # 设置等比例坐标轴
        ax.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax.spines.values():
            spine.set_linewidth(axis_line_width)

        if i == 0 and show_legend:
            legend = ax.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)
        if text_str:
            ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                    fontsize=10, verticalalignment='top', weight=bold_text,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    return fig, plot_files


def plot_virial_data(df, excel_file, output_dir, settings):
    """绘制维里张量数据的散点图"""
    # 确保有十八列数据
    if len(df.columns) < 18:
        raise ValueError("维里张量数据必须包含十八列")

    # 应用用户设置
    scatter_size = settings.get('scatter_size', 20)
    scatter_color = settings.get('scatter_color', 'blue')
    line_color = settings.get('line_color', 'red')
    line_width = settings.get('line_width', 2.0)
    scatter_label = settings.get('scatter_label', '数据点')
    line_label = settings.get('line_label', 'X=Y')
    plot_title = settings.get('plot_title', '')
    r_prefix = settings.get('r_prefix', 'R = ')
    rmse_prefix = settings.get('rmse_prefix', 'RMSE = ')
    decimal_places = settings.get('decimal_places', 3)
    axis_font_family = settings.get('axis_font_family', 'sans-serif')
    axis_font_size = settings.get('axis_font_size', 12)
    tick_font_family = settings.get('tick_font_family', 'sans-serif')
    tick_font_size = settings.get('tick_font_size', 10)
    axis_line_width = settings.get('axis_line_width', 1.0)
    show_r = settings.get('show_r', True)
    show_rmse = settings.get('show_rmse', True)
    show_title = settings.get('show_title', True)
    show_legend = settings.get('show_legend', True)

    # 字体加粗设置
    bold_axis = 'bold' if settings.get('bold_axis', True) else 'normal'
    bold_tick = 'bold' if settings.get('bold_tick', True) else 'normal'
    bold_legend = 'bold' if settings.get('bold_legend', True) else 'normal'
    bold_text = 'bold' if settings.get('bold_text', True) else 'normal'

    # 设置轴标题字体
    axis_font = {'family': axis_font_family, 'size': axis_font_size, 'weight': bold_axis}

    # 设置刻度字体
    tick_font = {'family': tick_font_family, 'size': tick_font_size, 'weight': bold_tick}

    # 如果没有提供标题，使用默认标题
    if not plot_title:
        filename = os.path.basename(excel_file)
        plot_title = f'DFT vs Deep Potential Virial Components: {filename}'

    # 分量标签
    components = ['XX', 'XY', 'XZ', 'YX', 'YY', 'YZ', 'ZX', 'ZY', 'ZZ']

    # 存储所有图像文件路径
    plot_files = []

    # 计算全局数据范围（所有维里分量）
    global_min = float('inf')
    global_max = float('-inf')

    # 遍历所有分量找出全局最小值和最大值
    for i in range(9):
        # 提取DFT分量和对应的DP预测分量
        dft_col = i
        dp_col = i + 9
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 更新全局范围
        min_val = min(x.min(), y.min())
        max_val = max(x.max(), y.max())

        if min_val < global_min:
            global_min = min_val
        if max_val > global_max:
            global_max = max_val

    # 扩展范围（增加10%的边距）
    margin = 0.1 * (global_max - global_min)
    plot_min = global_min - margin
    plot_max = global_max + margin

    # 创建图形（3x3网格）用于预览
    fig, axes = plt.subplots(3, 3, figsize=(18, 18))

    # 设置总标题（如果用户选择显示）
    if show_title:
        fig.suptitle(plot_title, fontsize=20, weight=bold_axis)

    # 绘制每个分量的散点图
    for i, comp in enumerate(components):
        row = i // 3
        col = i % 3
        ax = axes[row, col]

        # 提取数据：DFT分量和对应的DP预测分量
        dft_col = i
        dp_col = i + 9
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 绘制散点图
        ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)

        # 绘制X=Y直线
        line_x = np.linspace(plot_min, plot_max, 100)
        ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)

        # 设置坐标轴标签（添加单位）
        ax.set_xlabel(f'Virial({comp}) of DFT (eV/atom)', fontdict=axis_font)
        ax.set_ylabel(f'Virial({comp}) predicted by deep potential (eV/atom)', fontdict=axis_font)

        # 设置标题
        ax.set_title(f'Virial {comp} Component', fontsize=14, weight=bold_axis)

        # 设置坐标轴范围（使用全局范围）
        ax.set_xlim([plot_min, plot_max])
        ax.set_ylim([plot_min, plot_max])

        # 设置坐标轴比例相等
        ax.set_aspect('equal', adjustable='box')

        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax.spines.values():
            spine.set_linewidth(axis_line_width)

        # 添加图例（只在第一个子图添加）
        if i == 0 and show_legend:
            legend = ax.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)

        # 添加文本显示相关系数（如果用户选择显示）
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值，根据用户设置的小数位数
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

            if text_str:
                ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                        fontsize=10, verticalalignment='top', weight=bold_text,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout(rect=[0, 0, 1, 0.98])  # 为总标题留出空间

    # 保存组合图
    combined_file = os.path.join(output_dir, os.path.splitext(os.path.basename(excel_file))[0] + '_virial_combined.png')
    plt.savefig(combined_file, dpi=300, bbox_inches='tight')
    plot_files.append(combined_file)
    plt.close(fig)  # 关闭图形以释放内存

    # 创建并保存单独的图像（正方形）
    for i, comp in enumerate(components):
        # 创建新图形（正方形）
        fig_single, ax_single = plt.subplots(figsize=(8, 8))

        # 提取数据
        dft_col = i
        dp_col = i + 9
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 绘制散点图
        ax_single.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)

        # 绘制X=Y直线
        ax_single.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)

        # 设置坐标轴标签（添加单位）
        ax_single.set_xlabel(f'Virial({comp}) of DFT (eV/atom)', fontdict=axis_font)
        ax_single.set_ylabel(f'Virial({comp}) predicted by deep potential (eV/atom)', fontdict=axis_font)

        # 设置标题
        filename = os.path.basename(excel_file)
        if show_title:
            if plot_title:
                ax_single.set_title(f'Virial {comp} Component: {plot_title}', fontsize=14, weight=bold_axis)
            else:
                ax_single.set_title(f'Virial {comp} Component: {filename}', fontsize=14, weight=bold_axis)

        # 设置坐标轴范围（使用全局范围）
        ax_single.set_xlim([plot_min, plot_max])
        ax_single.set_ylim([plot_min, plot_max])

        # 设置坐标轴比例相等
        ax_single.set_aspect('equal', adjustable='box')

        # 添加网格
        ax_single.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax_single.get_xticklabels() + ax_single.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax_single.spines.values():
            spine.set_linewidth(axis_line_width)

        # 添加图例
        if show_legend:
            legend = ax_single.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)

        # 添加文本显示相关系数（如果用户选择显示）
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值，根据用户设置的小数位数
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

            if text_str:
                ax_single.text(0.05, 0.95, text_str, transform=ax_single.transAxes,
                               fontsize=10, verticalalignment='top', weight=bold_text,
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 保存单独图像
        plot_file = os.path.join(output_dir, os.path.splitext(filename)[0] + f'_virial_{comp}_plot.png')
        plt.tight_layout()
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plot_files.append(plot_file)
        plt.close(fig_single)

    # 重新打开图形以在GUI中预览
    fig, axes = plt.subplots(3, 3, figsize=(18, 18))
    if show_title:
        fig.suptitle(plot_title, fontsize=20, weight=bold_axis)

    # 绘制每个分量的散点图（用于预览）
    for i, comp in enumerate(components):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        dft_col = i
        dp_col = i + 9
        x = df.iloc[:, dft_col]
        y = df.iloc[:, dp_col]

        # 初始化文本字符串
        text_str = ""

        # 计算相关系数和RMSE
        if show_r or show_rmse:
            r_value = np.corrcoef(x, y)[0, 1]
            rmse = np.sqrt(np.mean((x - y) ** 2))

            # 格式化R和RMSE值
            fmt_str = f".{decimal_places}f"
            text_str = ""

            if show_r:
                r_value_str = format(r_value, fmt_str)
                text_str += f'{r_prefix}{r_value_str}\n'

            if show_rmse:
                rmse_str = format(rmse, fmt_str)
                text_str += f'{rmse_prefix}{rmse_str}'

            # 移除多余的换行符
            text_str = text_str.strip()

        ax.scatter(x, y, s=scatter_size, alpha=0.7, color=scatter_color, label=scatter_label)
        ax.plot(line_x, line_x, '--', color=line_color, label=line_label, linewidth=line_width)
        ax.set_xlabel(f'Virial({comp}) of DFT (eV/atom)', fontdict=axis_font)
        ax.set_ylabel(f'Virial({comp}) predicted by deep potential (eV/atom)', fontdict=axis_font)
        ax.set_title(f'Virial {comp} Component', fontsize=14, weight=bold_axis)
        ax.set_xlim([plot_min, plot_max])
        ax.set_ylim([plot_min, plot_max])
        ax.set_aspect('equal', adjustable='box')  # 设置等比例坐标轴
        ax.grid(True, linestyle='--', alpha=0.7)

        # 设置刻度字体
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontfamily(tick_font_family)
            label.set_fontsize(tick_font_size)
            label.set_fontweight(bold_tick)

        # 设置坐标轴线宽
        for spine in ax.spines.values():
            spine.set_linewidth(axis_line_width)

        if i == 0 and show_legend:
            legend = ax.legend()
            for text in legend.get_texts():
                text.set_fontweight(bold_legend)
        if text_str:
            ax.text(0.05, 0.95, text_str, transform=ax.transAxes,
                    fontsize=10, verticalalignment='top', weight=bold_text,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    return fig, plot_files


def browse_folder():
    """浏览并选择文件夹，然后列出其中的.out文件"""
    global current_folder
    folder_path = filedialog.askdirectory(title="选择包含.out文件的文件夹")
    if folder_path:
        current_folder = folder_path
        # 扫描文件夹中的.out文件
        out_files = [f for f in os.listdir(folder_path) if f.endswith('.out')]

        if not out_files:
            messagebox.showwarning("警告", "该文件夹中没有找到.out文件！")
            return

        # 更新文件选择下拉框
        file_combobox['values'] = out_files
        if out_files:
            file_combobox.set(out_files[0])
            input_entry.delete(0, tk.END)
            input_entry.insert(0, os.path.join(folder_path, out_files[0]))


def browse_file():
    """浏览并选择.out文件"""
    file_path = filedialog.askopenfilename(
        title="选择.out文件",
        filetypes=[("OUT files", "*.out"), ("All files", "*.*")]
    )
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)


def on_file_select(event):
    """当下拉框选择文件时更新输入框"""
    selected_file = file_var.get()
    if selected_file and current_folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, os.path.join(current_folder, selected_file))


def show_settings_dialog():
    """显示绘图设置对话框"""
    global current_settings  # 声明为全局变量以便更新

    # 使用当前设置打开对话框
    dialog = PlotSettingsDialog(app, "绘图设置", initial_settings=current_settings)

    # 如果用户点击了确定，更新设置并保存
    if hasattr(dialog, 'result'):
        current_settings = dialog.result
        save_settings(current_settings)
        messagebox.showinfo("设置已保存", "绘图设置已保存，将在下次运行时自动加载")


def save_settings(settings):
    """保存设置到文件"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"设置已保存到: {SETTINGS_FILE}")
    except Exception as e:
        messagebox.showerror("保存错误", f"保存设置时出错: {str(e)}")


def load_settings():
    """从文件加载设置，如果文件不存在则返回默认设置"""
    default_settings = {
        'scatter_size': 20,
        'scatter_color': 'blue',
        'line_color': 'red',
        'line_width': 2.0,
        'scatter_label': '数据点',
        'line_label': 'X=Y',
        'plot_title': '',
        'r_prefix': 'R = ',
        'rmse_prefix': 'RMSE = ',
        'decimal_places': 3,
        'axis_font_family': 'sans-serif',
        'axis_font_size': 12,
        'tick_font_family': 'sans-serif',
        'tick_font_size': 10,
        'axis_line_width': 1.0,
        'show_r': True,
        'show_rmse': True,
        'show_title': True,
        'show_legend': True,
        'bold_axis': True,  # 轴标题默认加粗
        'bold_tick': True,  # 刻度默认加粗
        'bold_legend': True,  # 图例默认加粗
        'bold_text': True  # 文本默认加粗
    }

    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        messagebox.showwarning("加载设置", f"加载设置时出错，将使用默认设置: {str(e)}")

    return default_settings


def process_file():
    """处理选择的文件并生成结果"""
    input_path = input_entry.get()
    if not input_path:
        status_label.config(text="请先选择文件！", fg="red")
        return

    try:
        # 转换文件
        output_file, num_cols, df = process_out_file(input_path)

        # 确保目录存在
        plot_dir = os.path.join(os.path.dirname(output_file), "plots")
        os.makedirs(plot_dir, exist_ok=True)

        # 根据数据类型绘图
        if num_cols == 2:
            # 能量数据
            fig, plot_files = plot_energy_data(df, output_file, plot_dir, current_settings)
            plot_type = "能量"
        elif num_cols == 6:
            # 力分量数据
            fig, plot_files = plot_force_data(df, output_file, plot_dir, current_settings)
            plot_type = "力分量"
        elif num_cols == 18:
            # 维里张量数据
            fig, plot_files = plot_virial_data(df, output_file, plot_dir, current_settings)
            plot_type = "维里张量"
        else:
            raise ValueError(f"不支持{num_cols}列的数据格式")

        # 显示结果
        files_text = "\n".join([f"• {os.path.basename(f)}" for f in plot_files])
        status_label.config(text=f"处理成功！\nExcel文件: {os.path.basename(output_file)}\n\n图表文件:\n{files_text}",
                            fg="green")

        # 显示图表预览
        show_plot_preview(fig)

    except Exception as e:
        status_label.config(text=f"处理失败: {str(e)}", fg="red")
        # 在控制台打印详细错误信息
        import traceback
        traceback.print_exc()


def show_plot_preview(fig):
    """在GUI中显示图表预览"""
    # 清除之前的预览
    for widget in preview_frame.winfo_children():
        widget.destroy()

    # 创建画布
    canvas = FigureCanvasTkAgg(fig, master=preview_frame)
    canvas.draw()

    # 添加工具栏
    toolbar = NavigationToolbar2Tk(canvas, preview_frame)
    toolbar.update()

    # 添加画布到界面
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


def on_closing():
    """处理窗口关闭事件"""
    app.destroy()
    sys.exit()


# 创建GUI
app = tk.Tk()
app.title("DFT与Deep Potential分析工具")
app.geometry("1200x900")  # 增加窗口大小以适应更多内容

# 加载设置
current_settings = load_settings()

# 存储当前选择的文件夹
current_folder = ""

# 绑定关闭事件
app.protocol("WM_DELETE_WINDOW", on_closing)

# 主框架
main_frame = tk.Frame(app)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 文件选择部分
file_frame = tk.LabelFrame(main_frame, text="文件处理")
file_frame.pack(fill=tk.X, padx=5, pady=5)

# 文件夹浏览按钮
folder_frame = tk.Frame(file_frame)
folder_frame.pack(fill=tk.X, pady=5)
tk.Button(folder_frame, text="浏览文件夹...", command=browse_folder).pack(side=tk.LEFT, padx=5)

# 文件选择下拉框
file_var = StringVar()
file_combobox = ttk.Combobox(folder_frame, textvariable=file_var, width=50, state="readonly")
file_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
file_combobox.bind("<<ComboboxSelected>>", on_file_select)

# 文件路径输入
tk.Label(file_frame, text="文件路径:").pack(anchor="w", padx=5, pady=(5, 0))
input_entry = tk.Entry(file_frame, width=80)
input_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
tk.Button(file_frame, text="浏览文件...", command=browse_file).pack(side=tk.LEFT, padx=5)

# 设置按钮
tk.Button(file_frame, text="绘图设置", command=show_settings_dialog, bg="#2196F3", fg="white").pack(side=tk.LEFT,
                                                                                                    padx=5)

# 处理按钮
btn_frame = tk.Frame(main_frame)
btn_frame.pack(fill=tk.X, padx=5, pady=10)
tk.Button(btn_frame, text="处理文件并绘图", command=process_file, width=20, height=2,
          bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

# 状态显示
status_frame = tk.LabelFrame(main_frame, text="处理状态")
status_frame.pack(fill=tk.X, padx=5, pady=5)
status_label = tk.Label(status_frame, text="等待处理文件...", wraplength=1100, justify=tk.LEFT, anchor="w")
status_label.pack(fill=tk.X, padx=10, pady=10)

# 预览区域
preview_frame = tk.LabelFrame(main_frame, text="图表预览")
preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# 初始显示说明
init_label = tk.Label(preview_frame, text="处理后将显示图表预览", font=("Arial", 14))
init_label.pack(expand=True)

app.mainloop()