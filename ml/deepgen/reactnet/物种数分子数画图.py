import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, font
import tkinter.scrolledtext as scrolledtext
import numpy as np

# 默认配置
DEFAULT_CONFIG = {
    "excel_file": "",
    "output_dir": "",
    "axis_width": 1.5,
    "line_width": 2.0,
    "label_fontsize": 14,
    "label_font": "Times New Roman",
    "legend_fontsize": 12,
    "legend_frame": True,
    "legend_border_width": 1.0,
    "xlabel": "Time (s)",
    "ylabel_species": "Number of Species",
    "ylabel_molecules": "Number of Molecules",
    "grid_style": "--",
    "grid_alpha": 0.7,
    "show_title": True,
    "title_fontsize": 16,
    "title_font": "Times New Roman",
    "custom_title": "",
    "species_title": "Number of Species over Time",
    "molecules_title": "Number of Molecules over Time"
}

CONFIG_FILE = "plot_settings.json"


class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel数据绘图工具")
        self.root.geometry("900x650")
        self.config = self.load_config()

        # 创建主框架 - 使用网格布局管理器
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置主网格
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # 文件区域
        self.main_frame.grid_rowconfigure(1, weight=0)  # 设置区域
        self.main_frame.grid_rowconfigure(2, weight=1)  # 预览区域
        self.main_frame.grid_rowconfigure(3, weight=0)  # 按钮区域

        # 创建各个区域
        self.create_file_section()
        self.create_settings_section()
        self.create_preview_section()
        self.create_button_section()

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("就绪")

        # 初始化标题设置状态
        self.toggle_title_settings()
        self.toggle_custom_title()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # 确保所有配置项都存在
                    for key in DEFAULT_CONFIG:
                        if key not in config:
                            config[key] = DEFAULT_CONFIG[key]
                    return config
            except:
                # 配置文件损坏时回退到默认配置
                messagebox.showerror("错误", "配置文件损坏，使用默认配置")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存当前配置到文件"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.status_var.set(f"配置已保存到: {CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存配置时出错: {str(e)}")

    def create_file_section(self):
        """创建文件选择区域"""
        file_frame = ttk.LabelFrame(self.main_frame, text="文件设置", padding="10")
        file_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        file_frame.columnconfigure(1, weight=1)

        # Excel文件选择
        ttk.Label(file_frame, text="Excel文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_entry = ttk.Entry(file_frame, width=60)
        self.file_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        if self.config["excel_file"]:
            self.file_entry.insert(0, self.config["excel_file"])

        ttk.Button(file_frame, text="浏览...", command=self.select_file).grid(row=0, column=2, padx=5, pady=5)

        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.dir_entry = ttk.Entry(file_frame, width=60)
        self.dir_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        if self.config["output_dir"]:
            self.dir_entry.insert(0, self.config["output_dir"])

        ttk.Button(file_frame, text="浏览...", command=self.select_output_dir).grid(row=1, column=2, padx=5, pady=5)

    def create_settings_section(self):
        """创建绘图设置区域"""
        settings_frame = ttk.LabelFrame(self.main_frame, text="绘图设置", padding="10")
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 使用Notebook组织设置
        self.settings_notebook = ttk.Notebook(settings_frame)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 第一页：轴线和标签
        axes_frame = ttk.Frame(self.settings_notebook, padding="5")
        self.settings_notebook.add(axes_frame, text="轴线和标签")

        # 第二页：标题和图例
        title_frame = ttk.Frame(self.settings_notebook, padding="5")
        self.settings_notebook.add(title_frame, text="标题和图例")

        # 第三页：网格和样式
        grid_frame = ttk.Frame(self.settings_notebook, padding="5")
        self.settings_notebook.add(grid_frame, text="网格和样式")

        # 填充各个设置页
        self.create_axes_settings(axes_frame)
        self.create_title_settings(title_frame)
        self.create_grid_settings(grid_frame)

    def create_axes_settings(self, frame):
        """创建轴线设置"""
        # 轴线设置
        ttk.Label(frame, text="坐标轴线宽:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.axis_width_var = tk.DoubleVar(value=self.config["axis_width"])
        ttk.Scale(frame, from_=0.5, to=5, orient=tk.HORIZONTAL,
                  variable=self.axis_width_var, length=200).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.axis_width_var).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(frame, text="数据线粗细:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.line_width_var = tk.DoubleVar(value=self.config["line_width"])
        ttk.Scale(frame, from_=0.5, to=5, orient=tk.HORIZONTAL,
                  variable=self.line_width_var, length=200).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.line_width_var).grid(row=1, column=2, padx=5, pady=2)

        # 标签设置
        ttk.Label(frame, text="X轴标签:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.xlabel_var = tk.StringVar(value=self.config["xlabel"])
        ttk.Entry(frame, textvariable=self.xlabel_var, width=30).grid(row=2, column=1, columnspan=2, sticky=tk.W,
                                                                      padx=5, pady=2)

        ttk.Label(frame, text="物种数Y轴标签:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.yspecies_var = tk.StringVar(value=self.config["ylabel_species"])
        ttk.Entry(frame, textvariable=self.yspecies_var, width=30).grid(row=3, column=1, columnspan=2, sticky=tk.W,
                                                                        padx=5, pady=2)

        ttk.Label(frame, text="分子数Y轴标签:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.ymolecules_var = tk.StringVar(value=self.config["ylabel_molecules"])
        ttk.Entry(frame, textvariable=self.ymolecules_var, width=30).grid(row=4, column=1, columnspan=2, sticky=tk.W,
                                                                          padx=5, pady=2)

        # 字体设置
        ttk.Label(frame, text="标签字体:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.font_var = tk.StringVar(value=self.config["label_font"])
        ttk.Combobox(frame, textvariable=self.font_var, width=20,
                     values=sorted(font.families())).grid(row=5, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame, text="标签字号:").grid(row=5, column=2, sticky=tk.W, padx=5, pady=2)
        self.fontsize_var = tk.IntVar(value=self.config["label_fontsize"])
        ttk.Spinbox(frame, from_=6, to=36, width=5, textvariable=self.fontsize_var).grid(row=5, column=3, padx=5,
                                                                                         pady=2)

    def create_title_settings(self, frame):
        """创建标题设置"""
        # 显示标题选项
        self.show_title_var = tk.BooleanVar(value=self.config["show_title"])
        ttk.Checkbutton(frame, text="显示图表标题", variable=self.show_title_var,
                        command=self.toggle_title_settings).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5,
                                                                 pady=2)

        # 自定义标题选项
        self.custom_title_var = tk.BooleanVar(value=bool(self.config["custom_title"]))
        ttk.Checkbutton(frame, text="使用自定义标题", variable=self.custom_title_var,
                        command=self.toggle_custom_title).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5,
                                                               pady=2)

        # 标题文本
        ttk.Label(frame, text="标题文本:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.title_var = tk.StringVar(value=self.config["custom_title"] or "")
        self.title_entry = ttk.Entry(frame, textvariable=self.title_var, width=40,
                                     state=tk.NORMAL if self.custom_title_var.get() else tk.DISABLED)
        self.title_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # 物种标题预设
        ttk.Label(frame, text="物种数标题预设:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.species_title_var = tk.StringVar(value=self.config["species_title"])
        ttk.Entry(frame, textvariable=self.species_title_var, width=40).grid(row=3, column=1, columnspan=3, sticky=tk.W,
                                                                             padx=5, pady=2)

        # 分子标题预设
        ttk.Label(frame, text="分子数标题预设:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.molecules_title_var = tk.StringVar(value=self.config["molecules_title"])
        ttk.Entry(frame, textvariable=self.molecules_title_var, width=40).grid(row=4, column=1, columnspan=3,
                                                                               sticky=tk.W, padx=5, pady=2)

        # 标题字体设置
        ttk.Label(frame, text="标题字体:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.title_font_var = tk.StringVar(value=self.config["title_font"])
        self.title_font_combo = ttk.Combobox(frame, textvariable=self.title_font_var, width=20,
                                             values=sorted(font.families()))
        self.title_font_combo.grid(row=5, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame, text="标题字号:").grid(row=5, column=2, sticky=tk.W, padx=5, pady=2)
        self.title_fontsize_var = tk.IntVar(value=self.config["title_fontsize"])
        self.title_fontsize_spin = ttk.Spinbox(frame, from_=10, to=36, width=5,
                                               textvariable=self.title_fontsize_var)
        self.title_fontsize_spin.grid(row=5, column=3, padx=5, pady=2)

        # 图例设置
        ttk.Label(frame, text="图例字号:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.legend_size_var = tk.IntVar(value=self.config["legend_fontsize"])
        ttk.Spinbox(frame, from_=6, to=24, width=5, textvariable=self.legend_size_var).grid(row=6, column=1, padx=5,
                                                                                            pady=2, sticky=tk.W)

        # 图例边框
        self.legend_frame_var = tk.BooleanVar(value=self.config["legend_frame"])
        ttk.Checkbutton(frame, text="显示图例边框", variable=self.legend_frame_var).grid(row=6, column=2, padx=5,
                                                                                         pady=2, sticky=tk.W)

        # 图例边框宽度
        ttk.Label(frame, text="图例边框宽度:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
        self.legend_border_width_var = tk.DoubleVar(value=self.config.get("legend_border_width", 1.0))
        ttk.Scale(frame, from_=0.5, to=3, orient=tk.HORIZONTAL,
                  variable=self.legend_border_width_var, length=150).grid(row=7, column=1, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.legend_border_width_var).grid(row=7, column=2, padx=5, pady=2)

    def create_grid_settings(self, frame):
        """创建网格设置"""
        # 网格设置
        ttk.Label(frame, text="网格样式:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.grid_style_var = tk.StringVar(value=self.config["grid_style"])
        ttk.Combobox(frame, textvariable=self.grid_style_var, width=10,
                     values=["-", "--", "-.", ":"]).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(frame, text="网格透明度:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.grid_alpha_var = tk.DoubleVar(value=self.config["grid_alpha"])
        ttk.Scale(frame, from_=0.1, to=1, orient=tk.HORIZONTAL,
                  variable=self.grid_alpha_var, length=100).grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(frame, textvariable=self.grid_alpha_var).grid(row=0, column=4, padx=5, pady=2)

        # 添加示例预览图
        self.preview_canvas = tk.Canvas(frame, width=300, height=150, bg='white')
        self.preview_canvas.grid(row=2, column=0, columnspan=5, padx=10, pady=10)
        self.draw_preview()

    def toggle_title_settings(self):
        """切换标题设置状态"""
        state = tk.NORMAL if self.show_title_var.get() else tk.DISABLED
        # 不再重置自定义标题选项，保留用户设置
        self.title_entry.config(state=state)
        self.title_font_combo.config(state=state)
        self.title_fontsize_spin.config(state=state)
        self.toggle_custom_title()

        # 只有在预览画布创建后才绘制预览
        if hasattr(self, 'preview_canvas'):
            self.draw_preview()

    def toggle_custom_title(self):
        """切换自定义标题状态"""
        if not self.show_title_var.get():
            return

        if self.custom_title_var.get():
            self.title_entry.config(state=tk.NORMAL)
            # 不清空预设标题，保留用户设置
        else:
            self.title_entry.config(state=tk.DISABLED)

    def create_preview_section(self):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(self.main_frame, text="预览", padding="10")
        preview_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        # 工作表预览
        ttk.Label(preview_frame, text="工作表预览:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        # 创建带滚动条的文本框
        text_frame = ttk.Frame(preview_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.preview_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        self.preview_text.config(state=tk.DISABLED)

    def create_button_section(self):
        """创建按钮区域 - 固定在底部"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=10)

        # 按钮容器
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(expand=True)

        # 添加按钮
        ttk.Button(btn_container, text="预览数据", command=self.preview_data).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(btn_container, text="生成图片", command=self.generate_plots).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(btn_container, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(btn_container, text="重置设置", command=self.reset_settings).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(btn_container, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=10, pady=5)

    def reset_settings(self):
        """重置为默认设置"""
        if messagebox.askyesno("重置设置", "确定要重置所有设置为默认值吗？"):
            self.config = DEFAULT_CONFIG.copy()
            # 更新UI控件
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, self.config["excel_file"])
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, self.config["output_dir"])
            self.axis_width_var.set(self.config["axis_width"])
            self.line_width_var.set(self.config["line_width"])
            self.xlabel_var.set(self.config["xlabel"])
            self.yspecies_var.set(self.config["ylabel_species"])
            self.ymolecules_var.set(self.config["ylabel_molecules"])
            self.font_var.set(self.config["label_font"])
            self.fontsize_var.set(self.config["label_fontsize"])
            self.legend_size_var.set(self.config["legend_fontsize"])
            self.legend_frame_var.set(self.config["legend_frame"])
            self.legend_border_width_var.set(self.config["legend_border_width"])
            self.grid_style_var.set(self.config["grid_style"])
            self.grid_alpha_var.set(self.config["grid_alpha"])
            self.show_title_var.set(self.config["show_title"])
            self.title_font_var.set(self.config["title_font"])
            self.title_fontsize_var.set(self.config["title_fontsize"])
            self.custom_title_var.set(bool(self.config["custom_title"]))
            self.title_var.set(self.config["custom_title"])
            self.species_title_var.set(self.config["species_title"])
            self.molecules_title_var.set(self.config["molecules_title"])

            self.toggle_title_settings()
            self.toggle_custom_title()

            if hasattr(self, 'preview_canvas'):
                self.draw_preview()

            self.status_var.set("设置已重置为默认值")

    def draw_preview(self):
        """在预览画布上绘制样式示例"""
        if not hasattr(self, 'preview_canvas'):
            return

        canvas = self.preview_canvas
        canvas.delete("all")

        # 绘制坐标轴
        canvas.create_line(50, 130, 250, 130, width=2)  # X轴
        canvas.create_line(50, 130, 50, 30, width=2)  # Y轴

        # 绘制刻度
        for i in range(1, 6):
            x = 50 + i * 40
            canvas.create_line(x, 130, x, 125, width=1)
            canvas.create_text(x, 140, text=str(i))

            y = 130 - i * 20
            canvas.create_line(50, y, 55, y, width=1)
            canvas.create_text(40, y, text=str(i * 10))

        # 绘制数据线
        points = [(50 + i * 40, 130 - (i % 5) * 20) for i in range(6)]
        canvas.create_line(points, fill="blue", width=2, smooth=True)

        # 绘制图例
        legend_border_width = self.legend_border_width_var.get() if hasattr(self, 'legend_border_width_var') else 1.0
        canvas.create_rectangle(180, 40, 240, 70, outline="black", width=legend_border_width)
        canvas.create_line(185, 55, 200, 55, fill="blue", width=2)
        canvas.create_text(215, 55, text="数据线", anchor=tk.W)

        # 如果启用了标题，则绘制标题
        if self.show_title_var.get():
            title = self.title_var.get() if self.custom_title_var.get() else "图表标题"
            canvas.create_text(150, 15, text=title, font=("Arial", 10, "bold"))

        # 绘制标签
        canvas.create_text(150, 150, text="X轴标签", anchor=tk.N)
        canvas.create_text(20, 80, text="Y轴标签", angle=90)

    def select_file(self):
        """选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

            # 自动设置输出目录为Excel文件所在目录
            output_dir = os.path.dirname(file_path)
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, output_dir)
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择图片输出目录")
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)
            self.status_var.set(f"输出目录: {dir_path}")

    def preview_data(self):
        """预览Excel数据"""
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择Excel文件")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return

        try:
            # 读取Excel文件
            xl = pd.ExcelFile(file_path)

            # 显示工作表信息
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)

            self.preview_text.insert(tk.END, f"Excel文件: {os.path.basename(file_path)}\n")
            self.preview_text.insert(tk.END, f"工作表列表: {xl.sheet_names}\n\n")

            # 不区分大小写匹配工作表
            species_sheets = [name for name in xl.sheet_names if "number of species" in name.lower()]
            molecules_sheets = [name for name in xl.sheet_names if "number of molecules" in name.lower()]

            # 预览物种工作表
            if species_sheets:
                sheet_name = species_sheets[0]
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                self.preview_text.insert(tk.END, f"工作表 '{sheet_name}' 预览 (前5行):\n")
                self.preview_text.insert(tk.END, df.head().to_string() + "\n\n")
            else:
                self.preview_text.insert(tk.END, "警告: 未找到物种数量工作表\n\n")

            # 预览分子工作表
            if molecules_sheets:
                sheet_name = molecules_sheets[0]
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                self.preview_text.insert(tk.END, f"工作表 '{sheet_name}' 预览 (前5行):\n")
                self.preview_text.insert(tk.END, df.head().to_string() + "\n\n")
            else:
                self.preview_text.insert(tk.END, "警告: 未找到分子数量工作表\n\n")

            self.preview_text.config(state=tk.DISABLED)
            self.status_var.set(f"数据预览完成: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("错误", f"读取Excel文件时出错: {str(e)}")

    def generate_plots(self):
        """生成图片"""
        # 收集所有设置
        self.config["excel_file"] = self.file_entry.get()
        self.config["output_dir"] = self.dir_entry.get()
        self.config["axis_width"] = self.axis_width_var.get()
        self.config["line_width"] = self.line_width_var.get()
        self.config["xlabel"] = self.xlabel_var.get()
        self.config["ylabel_species"] = self.yspecies_var.get()
        self.config["ylabel_molecules"] = self.ymolecules_var.get()
        self.config["label_font"] = self.font_var.get()
        self.config["label_fontsize"] = self.fontsize_var.get()
        self.config["legend_fontsize"] = self.legend_size_var.get()
        self.config["legend_frame"] = self.legend_frame_var.get()
        self.config["legend_border_width"] = self.legend_border_width_var.get()
        self.config["grid_style"] = self.grid_style_var.get()
        self.config["grid_alpha"] = self.grid_alpha_var.get()
        self.config["show_title"] = self.show_title_var.get()
        self.config["title_font"] = self.title_font_var.get()
        self.config["title_fontsize"] = self.title_fontsize_var.get()
        self.config["custom_title"] = self.title_var.get()
        self.config["species_title"] = self.species_title_var.get()
        self.config["molecules_title"] = self.molecules_title_var.get()

        # 验证设置
        if not self.config["excel_file"]:
            messagebox.showwarning("警告", "请选择Excel文件")
            return

        if not os.path.exists(self.config["excel_file"]):
            messagebox.showerror("错误", f"文件不存在: {self.config['excel_file']}")
            return

        output_dir = self.config["output_dir"]
        if not output_dir:
            # 默认使用Excel文件所在目录
            output_dir = os.path.dirname(self.config["excel_file"])
            self.config["output_dir"] = output_dir
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, output_dir)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 保存当前配置
        self.save_config()

        # 构建输出路径
        base_name = os.path.splitext(os.path.basename(self.config["excel_file"]))[0]
        species_path = os.path.join(output_dir, f"{base_name}_species.png")
        molecules_path = os.path.join(output_dir, f"{base_name}_molecules.png")

        try:
            # 处理物种数量工作表
            species_title = self.get_title("species")
            success_species = self.plot_sheet_data(
                sheet_names=["Number of species", "number of species"],  # 支持多种可能的大小写
                output_image_path=species_path,
                ylabel=self.config["ylabel_species"],
                title=species_title
            )

            # 处理分子数量工作表
            molecules_title = self.get_title("molecules")
            success_molecules = self.plot_sheet_data(
                sheet_names=["number of molecules", "Number of molecules"],  # 支持多种可能的大小写
                output_image_path=molecules_path,
                ylabel=self.config["ylabel_molecules"],
                title=molecules_title
            )

            if success_species and success_molecules:
                self.status_var.set(f"图片已生成: {os.path.basename(species_path)}, {os.path.basename(molecules_path)}")
                messagebox.showinfo("完成", f"图片已保存到:\n{species_path}\n{molecules_path}")
            elif success_species:
                self.status_var.set(f"部分图片已生成: {os.path.basename(species_path)}")
                messagebox.showinfo("完成", f"物种图表已保存到:\n{species_path}\n但未找到分子数量工作表")
            elif success_molecules:
                self.status_var.set(f"部分图片已生成: {os.path.basename(molecules_path)}")
                messagebox.showinfo("完成", f"分子图表已保存到:\n{molecules_path}\n但未找到物种数量工作表")
            else:
                messagebox.showerror("错误", "未能生成任何图表，请检查工作表是否存在")
        except Exception as e:
            messagebox.showerror("错误", f"生成图表时发生错误: {str(e)}")

    def get_title(self, chart_type):
        """获取图表标题"""
        if not self.config["show_title"]:
            return ""

        if self.config["custom_title"]:
            return self.config["custom_title"]

        if chart_type == "species":
            return self.config["species_title"]
        else:
            return self.config["molecules_title"]

    def plot_sheet_data(self, sheet_names, output_image_path, ylabel, title=""):
        """绘制工作表数据"""
        try:
            # 尝试匹配多个可能的工作表名称
            xl = pd.ExcelFile(self.config["excel_file"])
            actual_sheet_name = None
            for name in sheet_names:
                if name in xl.sheet_names:
                    actual_sheet_name = name
                    break

            if actual_sheet_name is None:
                # 尝试不区分大小写匹配
                for name in xl.sheet_names:
                    if name.lower() in [n.lower() for n in sheet_names]:
                        actual_sheet_name = name
                        break

            if actual_sheet_name is None:
                self.status_var.set(f"未找到工作表: {', '.join(sheet_names)}")
                return False

            # 读取Excel工作表
            df = pd.read_excel(self.config["excel_file"], sheet_name=actual_sheet_name)

            if df.empty:
                self.status_var.set(f"工作表 '{actual_sheet_name}' 为空")
                return False

            # 创建图表
            plt.figure(figsize=(10, 6))
            ax = plt.gca()

            # 设置坐标轴线宽
            for spine in ax.spines.values():
                spine.set_linewidth(self.config["axis_width"])

            # 绘制每条数据线
            time_col = df.columns[0]  # 第一列作为时间列
            for col in df.columns[1:]:
                plt.plot(df[time_col], df[col], linewidth=self.config["line_width"], label=col)

            # 设置坐标轴标签和字体
            font_prop = fm.FontProperties(
                family=self.config["label_font"],
                size=self.config["label_fontsize"]
            )
            plt.xlabel(self.config["xlabel"], fontproperties=font_prop)
            plt.ylabel(ylabel, fontproperties=font_prop)

            # 设置刻度标签字体 - 使用与标签相同的字号
            plt.xticks(fontname=self.config["label_font"], fontsize=self.config["label_fontsize"])
            plt.yticks(fontname=self.config["label_font"], fontsize=self.config["label_fontsize"])

            # 设置图例
            legend_prop = fm.FontProperties(
                family=self.config["label_font"],
                size=self.config["legend_fontsize"]
            )
            legend = plt.legend(prop=legend_prop, frameon=self.config["legend_frame"])
            if self.config["legend_frame"]:
                legend.get_frame().set_linewidth(self.config["legend_border_width"])

            # 添加网格线
            plt.grid(True, linestyle=self.config["grid_style"], alpha=self.config["grid_alpha"])

            # 添加标题（如果启用）
            if title:
                title_prop = fm.FontProperties(
                    family=self.config["title_font"],
                    size=self.config["title_fontsize"]
                )
                plt.title(title, fontproperties=title_prop)

            # 自动调整布局
            plt.tight_layout()

            # 保存图表
            plt.savefig(output_image_path, dpi=300)
            plt.close()

            self.status_var.set(f"图表 '{actual_sheet_name}' 已保存至: {output_image_path}")
            return True

        except Exception as e:
            self.status_var.set(f"处理工作表时出错: {str(e)}")
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()