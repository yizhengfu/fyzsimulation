import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
import networkx as nx
import random
from pyvis.network import Network
import openbabel as ob
import os
import datetime
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image  # 用于图片裁剪

# 尝试导入webdriver_manager，但不强制要求安装
try:
    from webdriver_manager.chrome import ChromeDriverManager

    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False


def setup_driver():
    """设置并返回WebDriver实例"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        # 尝试使用已安装的ChromeDriver
        driver = webdriver.Chrome(options=chrome_options)
        return driver, None
    except Exception as e:
        # 如果安装了webdriver_manager，则尝试自动下载
        if HAS_WEBDRIVER_MANAGER:
            try:
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
                return driver, None
            except Exception as e2:
                return None, f"WebDriver初始化失败: {str(e2)}"
        else:
            return None, "WebDriver初始化失败: 请确保已正确安装ChromeDriver或安装webdriver_manager包"


def crop_image(image_path):
    """裁剪图片，移除多余的白边"""
    try:
        # 打开图片
        img = Image.open(image_path)

        # 获取图片的边界框 (非白色区域)
        bbox = img.getbbox()

        if bbox:
            # 裁剪图片
            cropped_img = img.crop(bbox)

            # 覆盖原始图片
            cropped_img.save(image_path)
            return True
        return False
    except Exception as e:
        print(f"图片裁剪失败: {str(e)}")
        return False


def capture_html_as_image(html_path, output_image_path, wait_time=15, driver=None):
    """将HTML文件截图保存为PNG图片并裁剪白边"""
    if driver is None:
        return False, "WebDriver未初始化"

    try:
        # 加载HTML文件
        driver.get(f"file://{html_path}")

        # 等待网络图渲染完成 - 增加等待时间和容错
        try:
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, "vis-network"))
            )
        except:
            # 即使找不到元素也继续
            pass

        # 等待额外时间确保完全渲染
        time.sleep(1.0)  # 增加等待时间

        # 保存截图
        driver.save_screenshot(output_image_path)

        # 裁剪多余白边
        crop_image(output_image_path)

        return True, None
    except Exception as e:
        return False, f"截图失败: {str(e)}"


def process_single_reaction(filepath, target_smiles=None, threshold=10, reactnet_folder=None,
                            export_image=False, driver=None):
    """处理单个.reaction文件，并可选导出高清图片"""
    try:
        G = nx.DiGraph()
        all_reactions = []

        # 读取文件
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return None, None, f"文件读取失败: {str(e)}"

        # 解析反应数据并过滤
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' ', 1)
            if len(parts) != 2:
                continue
            try:
                frequency = int(parts[0])
                reaction = parts[1]
            except ValueError:
                continue
            if '->' not in reaction:
                continue
            reactant, product = reaction.split('->', 1)
            reactant = reactant.strip()
            product = product.strip()
            if (not target_smiles or target_smiles in (reactant, product)) and frequency > threshold:
                all_reactions.append((frequency, reactant, product))

        if not all_reactions:
            return None, None, "无符合条件的反应数据（频率或SMILES不满足）"

        # 合并重复反应（累加频率）
        reaction_df = pd.DataFrame(all_reactions, columns=['Frequency', 'Reactant', 'Product'])
        reaction_df = reaction_df.groupby(['Reactant', 'Product'], as_index=False)['Frequency'].sum()

        # 构建反应网络
        for _, row in reaction_df.iterrows():
            G.add_node(row['Reactant'])
            G.add_node(row['Product'])
            G.add_edge(row['Reactant'], row['Product'], frequency=row['Frequency'])

        # 提取分子公式
        intermediates = list(set(reaction_df['Reactant']) | set(reaction_df['Product']))
        formula_dict = {}
        for smi in intermediates:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                formula = rdMolDescriptors.CalcMolFormula(mol)
            else:
                try:
                    ob_conv = ob.OBConversion()
                    ob_conv.SetInAndOutFormats("smi", "can")
                    mol_ob = ob.OBMol()
                    ob_conv.ReadString(mol_ob, smi)
                    formula = mol_ob.GetFormula() if mol_ob.NumAtoms() > 0 else "未知"
                except:
                    formula = "未知"
            formula_dict[smi] = formula

        # 生成输出路径
        file_dir = os.path.dirname(filepath)
        current_dir_name = os.path.basename(file_dir)
        parent_dir_name = os.path.basename(os.path.dirname(file_dir)) if os.path.dirname(file_dir) else "root"

        # 目标文件名
        base_filename = f"trj_network_{threshold}_{current_dir_name}_{parent_dir_name}"
        html_path = os.path.join(reactnet_folder, f"{base_filename}.html")
        image_path = os.path.join(reactnet_folder, f"{base_filename}.png") if export_image else None

        # 生成并保存网络文件
        net = Network(notebook=True, directed=True, height="750px", width="100%")
        for smi in intermediates:
            net.add_node(
                smi,
                title=smi,
                label=formula_dict[smi],
                color=random.choice(['#FFB6C1', '#FFA07A', '#FFFACD', '#90EE90', '#87CEFA', '#D8BFD8']),
                size=20 + node_size_increment.get()
            )
        for u, v, d in G.edges(data=True):
            freq = d['frequency']
            net.add_edge(
                u, v,
                title=f"频率: {freq}",
                width=1.0 + line_width_increment.get() + (freq // 100) * 0.5
            )
        net.show_buttons(filter_=['physics'])
        net.save_graph(html_path)

        # 导出高清图片
        image_result = None
        if export_image and driver:
            success, error = capture_html_as_image(html_path, image_path, driver=driver)
            if success:
                image_result = image_path
            else:
                image_result = f"图片导出失败: {error}"

        return html_path, image_result, None
    except Exception as e:
        error_msg = f"处理文件 {os.path.basename(filepath)} 时发生错误: {str(e)}\n{traceback.format_exc()}"
        return None, None, error_msg


def analyze_folder():
    """分析文件夹内所有.reaction文件"""
    try:
        folder_path = folder_entry.get()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择文件夹！")
            return

        target_smiles = smiles_input.get().strip()

        try:
            threshold = int(threshold_input.get())
            if threshold < 0:
                raise ValueError("阈值不能为负数")
        except ValueError as e:
            messagebox.showerror("输入错误", f"频率阈值必须为非负整数！\n错误详情: {str(e)}")
            return

        # 获取导出图片设置
        export_image = export_image_var.get()

        # 初始化WebDriver（如果需要截图）
        driver = None
        if export_image:
            driver, driver_error = setup_driver()
            if driver_error:
                messagebox.showwarning("截图功能警告",
                                       f"无法初始化浏览器截图功能:\n{driver_error}\n将仅生成HTML文件。")
                export_image = False

        # 创建目标保存文件夹
        reactnet_folder = os.path.join(folder_path, f"reactnet_{threshold}_frequence")
        os.makedirs(reactnet_folder, exist_ok=True)

        # 初始化日志
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(folder_path, f"log_{threshold}_thresh_{timestamp}.txt")
        log_content = [
            f"处理时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"根文件夹: {folder_path}\n",
            f"目标保存文件夹: {reactnet_folder}\n",
            f"筛选条件: 频率>{threshold}, SMILES={target_smiles if target_smiles else '无'}\n",
            f"导出图片: {'是' if export_image else '否'}\n",
            "处理结果:\n"
        ]

        # 扫描所有.reaction文件
        reaction_files = []
        for root, dirs, files in os.walk(folder_path):
            # 跳过reactnet_开头的文件夹
            dirs[:] = [d for d in dirs if not d.startswith("reactnet_")]
            for file in files:
                if file.endswith('.reaction'):
                    full_path = os.path.join(root, file)
                    reaction_files.append(full_path)

        if not reaction_files:
            messagebox.showwarning("提示", "未找到任何.reaction文件！")
            return

        # 更新界面状态
        text_output.delete('1.0', tk.END)
        text_output.insert(tk.END, f"开始处理 {len(reaction_files)} 个文件（阈值={threshold}）...\n")
        if export_image:
            text_output.insert(tk.END, f"将导出高清图片并自动裁剪白边\n")
        status_bar.config(text=f"处理中: 0/{len(reaction_files)}")
        root_window.update()  # 使用正确的窗口引用更新界面

        # 逐个处理文件
        success_count = 0
        image_success_count = 0
        for idx, filepath in enumerate(reaction_files, 1):
            # 更新状态
            status_bar.config(text=f"处理中: {idx}/{len(reaction_files)}")
            text_output.insert(tk.END, f"\n文件 {idx}/{len(reaction_files)}: {os.path.basename(filepath)}... ")
            text_output.see(tk.END)
            text_output.update_idletasks()
            root_window.update()  # 使用正确的窗口引用更新界面

            try:
                html_path, image_path, error = process_single_reaction(
                    filepath, target_smiles, threshold, reactnet_folder,
                    export_image, driver
                )
            except Exception as e:
                error = f"处理过程中发生未捕获的异常: {str(e)}\n{traceback.format_exc()}"
                html_path, image_path = None, None

            if error:
                log_content.append(f"❌ {filepath} - 错误: {error}\n")
                text_output.insert(tk.END, f"失败（{error}）\n")
            else:
                log_content.append(f"✅ {filepath} - HTML: {html_path}\n")
                if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                    log_content.append(f"    ⬤ 图片: {image_path}\n")
                    text_output.insert(tk.END, f"成功（HTML和图片已保存）\n")
                    image_success_count += 1
                elif image_path:
                    log_content.append(f"    ⚠ 图片导出失败: {image_path}\n")
                    text_output.insert(tk.END, f"成功（HTML已保存，但图片导出失败）\n")
                else:
                    text_output.insert(tk.END, f"成功（HTML已保存）\n")
                success_count += 1

            # 写入部分日志，避免程序崩溃丢失所有进度
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(log_content)

            text_output.see(tk.END)
            text_output.update_idletasks()
            root_window.update()  # 使用正确的窗口引用更新界面

        # 关闭WebDriver
        if driver:
            try:
                driver.quit()
            except:
                pass

        # 写入最终日志
        with open(log_path, 'w', encoding='utf-8') as f:
            f.writelines(log_content)
            f.write(f"\n总结: 成功{success_count}个，失败{len(reaction_files) - success_count}个")
            if export_image:
                f.write(f", 图片导出成功{image_success_count}个")

        text_output.insert(tk.END, f"\n处理完成！共处理 {len(reaction_files)} 个文件，成功 {success_count} 个\n")
        text_output.insert(tk.END, f"日志文件: {log_path}\n")
        status_bar.config(text=f"处理完成（成功{success_count}个）")
        open_button.config(state=tk.NORMAL, command=lambda: os.startfile(reactnet_folder))

    except Exception as e:
        error_msg = f"处理过程中发生严重错误: {str(e)}\n{traceback.format_exc()}"
        messagebox.showerror("程序错误", error_msg)
        text_output.insert(tk.END, f"\n严重错误: {error_msg}\n")
        status_bar.config(text="处理失败")


# 主界面布局
root_window = tk.Tk()  # 修改变量名为 root_window
root_window.title("反应网络分析工具")
root_window.geometry("950x950")

# 定义全局变量（在创建控件前）
node_size_increment = tk.DoubleVar(value=10.0)
line_width_increment = tk.DoubleVar(value=1.0)
export_image_var = tk.BooleanVar(value=True)

# 文件夹选择框架
folder_frame = tk.Frame(root_window)
folder_frame.pack(pady=10, padx=10, fill=tk.X)
tk.Label(folder_frame, text="选择文件夹:").pack(side=tk.LEFT)
folder_entry = tk.Entry(folder_frame, width=60)
folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
tk.Button(folder_frame, text="浏览", command=lambda: [
    folder_entry.delete(0, tk.END),
    folder_entry.insert(0, filedialog.askdirectory()),
    status_bar.config(text=f"已选择: {folder_entry.get()}")
]).pack(side=tk.LEFT)

# SMILES筛选输入框架
smiles_frame = tk.Frame(root_window)
smiles_frame.pack(pady=10, padx=10, fill=tk.X)
tk.Label(smiles_frame, text="筛选SMILES（可选）:").pack(side=tk.LEFT)
smiles_input = tk.Entry(smiles_frame, width=60)
smiles_input.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

# 频率阈值输入框架
threshold_frame = tk.Frame(root_window)
threshold_frame.pack(pady=10, padx=10, fill=tk.X)
tk.Label(threshold_frame, text="频率阈值（保留>此值的反应）:").pack(side=tk.LEFT)
threshold_input = tk.Entry(threshold_frame, width=10)
threshold_input.pack(side=tk.LEFT, padx=5)
threshold_input.insert(0, "10")
tk.Label(threshold_frame, text="（整数，≥0）", fg="gray").pack(side=tk.LEFT, padx=5)

# 可视化参数设置框架
control_frame = tk.LabelFrame(root_window, text="可视化设置", padx=10, pady=10)
control_frame.pack(pady=10, padx=10, fill=tk.X)

# 节点大小增量滑块
tk.Label(control_frame, text="节点大小增量:").pack(side=tk.LEFT)
tk.Scale(
    control_frame,
    from_=0, to=50,
    variable=node_size_increment,
    orient=tk.HORIZONTAL,
    length=200
).pack(side=tk.LEFT, padx=5)

# 线条粗细增量滑块
tk.Label(control_frame, text="线条粗细增量:").pack(side=tk.LEFT)
tk.Scale(
    control_frame,
    from_=0, to=5,
    resolution=0.1,
    variable=line_width_increment,
    orient=tk.HORIZONTAL,
    length=200
).pack(side=tk.LEFT, padx=5)

# 截图设置框架
image_frame = tk.LabelFrame(root_window, text="高清图片导出设置", padx=10, pady=10)
image_frame.pack(pady=10, padx=10, fill=tk.X)

# 导出图片复选框
tk.Checkbutton(image_frame, text="导出高清PNG图片并自动裁剪白边", variable=export_image_var).pack(side=tk.LEFT, padx=5)

# 操作按钮框架
button_frame = tk.Frame(root_window)
button_frame.pack(pady=20)
tk.Button(
    button_frame,
    text="开始分析",
    command=analyze_folder,
    bg="#4CAF50", fg="white",
    width=15, height=2
).pack(side=tk.LEFT, padx=10)
open_button = tk.Button(
    button_frame,
    text="打开结果",
    state=tk.DISABLED,
    bg="#2196F3", fg="white",
    width=15, height=2
)
open_button.pack(side=tk.LEFT, padx=10)

# 处理日志显示框架
text_frame = tk.LabelFrame(root_window, text="处理日志", padx=10, pady=10)
text_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
text_output = tk.Text(text_frame, height=20)
text_output.pack(fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(text_output)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_output.yview)

# 状态栏
status_bar = tk.Label(root_window, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root_window.mainloop()