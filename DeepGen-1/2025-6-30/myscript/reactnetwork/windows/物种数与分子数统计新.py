import os
import shutil
import re
import pandas as pd
from tkinter import Tk, ttk, StringVar, filedialog, messagebox
from tkinter.ttk import Label, Button


class SpeciesAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("物种数分析工具（完整功能版）")

        # 界面变量
        self.target_folder = StringVar()
        self.status = StringVar(value="等待操作...")
        self.chemical = StringVar()  # 存储输入的化学式

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 文件夹选择区域
        Label(self.root, text="目标文件夹：").grid(row=0, column=0, padx=5, pady=5)
        self.folder_entry = ttk.Entry(self.root, textvariable=self.target_folder, width=50)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)
        Button(self.root, text="选择文件夹", command=self.select_folder).grid(row=0, column=2, padx=5, pady=5)

        # 原始分析按钮（文件转换）
        Button(self.root, text="开始分析", command=self.process_files).grid(row=1, column=1, pady=10)

        # 化学式查询区域
        Label(self.root, text="化学式：").grid(row=2, column=0, padx=5, pady=5)
        self.chemical_entry = ttk.Entry(self.root, textvariable=self.chemical, width=30)
        self.chemical_entry.grid(row=2, column=1, padx=5, pady=5)
        Button(self.root, text="分析化学式", command=self.search_chemical).grid(row=2, column=2, padx=5, pady=5)

        # 物种数统计区域
        Label(self.root, text="物种数和分子数统计：").grid(row=3, column=0, padx=5, pady=5)
        Button(self.root, text="分析", command=self.process_statistics).grid(row=3, column=2, padx=5, pady=5)

        # 反应物统计区域
        Label(self.root, text="反应物统计：").grid(row=4, column=0, padx=5, pady=5)
        Button(self.root, text="分析", command=self.process_reactants).grid(row=4, column=2, padx=5, pady=5)

        # 状态显示
        Label(self.root, text="状态：").grid(row=5, column=0, padx=5, pady=5)
        Label(self.root, textvariable=self.status).grid(row=5, column=1, columnspan=2, padx=5, pady=5)

    def select_folder(self):
        """选择目标文件夹"""
        folder = filedialog.askdirectory(title="选择包含子文件夹的根目录")
        if folder:
            self.target_folder.set(folder)
            self.status.set(f"已选择文件夹：{folder}")

    def process_files(self):
        """核心功能：原始文件转换（.species → .txt/.xlsx）"""
        root_dir = self.target_folder.get()
        if not root_dir:
            messagebox.showwarning("提示", "请先选择目标文件夹！")
            return

        output_dir = os.path.join(root_dir, "物种分析")
        os.makedirs(output_dir, exist_ok=True)

        processed = 0
        errors = []

        try:
            # 遍历根目录下的所有子文件夹
            subfolders = [f for f in os.listdir(root_dir)
                          if os.path.isdir(os.path.join(root_dir, f))]

            for subfolder in subfolders:
                subfolder_path = os.path.join(root_dir, subfolder)
                species_files = [f for f in os.listdir(subfolder_path)
                                 if f.endswith(".species")]
                if not species_files:
                    errors.append(f"子文件夹 '{subfolder}' 无.species文件")
                    continue

                # 处理第一个.species文件（假设唯一）
                src_file = os.path.join(subfolder_path, species_files[0])
                txt_dest = os.path.join(output_dir, f"{subfolder}.txt")
                xlsx_dest = os.path.join(output_dir, f"{subfolder}.xlsx")

                try:
                    # 复制并重命名为.txt
                    shutil.copy2(src_file, txt_dest)

                    # 解析文件内容
                    with open(txt_dest, 'r', encoding='utf-8') as f:
                        content = f.read()

                    timestep_data = self.parse_timestep_data(content)
                    if not timestep_data:
                        errors.append(f"{subfolder}.txt 无有效时间步数据")
                        continue

                    # 计算最大结构对数（确定列数）
                    max_pairs = max(len(pairs) for pairs in timestep_data.values()) if timestep_data else 0
                    if max_pairs == 0:
                        errors.append(f"{subfolder}.txt 无有效结构-数量对")
                        continue

                    # 生成Excel列名
                    columns = ["时间步"]
                    for i in range(1, max_pairs + 1):
                        columns.append(f"化学式{i}")
                        columns.append(f"数量{i}")

                    # 构建数据行
                    df_rows = []
                    for ts_num in sorted(timestep_data.keys()):
                        pairs = timestep_data[ts_num]
                        row = [ts_num]
                        for i in range(max_pairs):
                            if i < len(pairs):
                                row.append(pairs[i][0])  # 化学式
                                row.append(pairs[i][1])  # 数量
                            else:
                                row.append(None)
                                row.append(None)
                        df_rows.append(row)

                    # 保存为Excel
                    df = pd.DataFrame(df_rows, columns=columns)
                    df.to_excel(xlsx_dest, index=False)
                    processed += 1
                    self.status.set(f"处理中：已处理 {processed} 个文件")

                except Exception as e:
                    errors.append(f"子文件夹 '{subfolder}' 处理失败：{str(e)}")

            # 显示处理结果
            result_msg = f"处理完成！成功处理 {processed} 个文件\n"
            if errors:
                result_msg += "\n以下文件处理异常：\n" + "\n".join(errors)
            messagebox.showinfo("处理结果", result_msg)
            self.status.set(f"处理完成：成功 {processed} 个，异常 {len(errors)} 个")

        except Exception as e:
            messagebox.showerror("严重错误", f"程序运行失败：{str(e)}")
            self.status.set("处理失败")

    def parse_timestep_data(self, content):
        """
        解析.species文件内容，提取时间步和结构数据
        使用改进的SMILES格式解析逻辑
        """
        timestep_dict = {}
        # 匹配时间步及其内容
        timestep_pattern = re.compile(r'Timestep (\d+):(.*?)(?=Timestep \d+:|$)', re.DOTALL)

        # 匹配SMILES分子式和数量的对
        # 分子式可以包含字母、数字、括号、方括号、等号、百分号等SMILES允许的字符
        # 数量是紧随分子式后的整数
        structure_pattern = re.compile(r'([^\s]+?)\s+(\d+)(?=\s|$)')

        timesteps = timestep_pattern.findall(content)
        for ts_num, ts_content in timesteps:
            ts_num = int(ts_num)
            structures = []

            # 使用正则表达式查找所有匹配的分子式-数量对
            matches = structure_pattern.findall(ts_content)

            # 处理匹配结果
            for chem, count in matches:
                # 检查分子式是否有效（至少包含一个方括号或化学元素）
                if '[' in chem or any(c.isalpha() for c in chem):
                    structures.append((chem, int(count)))

            if structures:
                timestep_dict[ts_num] = structures

        return timestep_dict

    def search_chemical(self):
        """功能：化学式跨文件查询"""
        chemical = self.chemical.get().strip()
        if not chemical:
            messagebox.showwarning("提示", "请输入需要查询的化学式！")
            return

        root_dir = self.target_folder.get()
        if not root_dir:
            messagebox.showwarning("提示", "请先选择目标文件夹！")
            return

        species_dir = os.path.join(root_dir, "物种分析")
        if not os.path.exists(species_dir):
            messagebox.showwarning("提示", "未找到'物种分析'文件夹，请先运行初始分析！")
            return

        # 仅处理原始转换生成的文件（子文件夹名.xlsx）
        subfolders = [f for f in os.listdir(root_dir)
                      if os.path.isdir(os.path.join(root_dir, f))]
        original_files = [f"{subfolder}.xlsx" for subfolder in subfolders]
        xlsx_files = [f for f in os.listdir(species_dir)
                      if f.endswith(".xlsx") and f in original_files]

        if not xlsx_files:
            messagebox.showwarning("提示", "未找到原始转换生成的xlsx文件！")
            return

        # 初始化数据存储
        timestep_data = {}  # {timestep: {文件名（无后缀）: count}}
        all_timesteps = set()
        file_names = [os.path.splitext(f)[0] for f in xlsx_files]  # 去.xlsx后缀

        # 遍历文件查询化学式
        for idx, filename in enumerate(xlsx_files):
            file_path = os.path.join(species_dir, filename)
            current_file_name = file_names[idx]

            try:
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    ts = row["时间步"]
                    all_timesteps.add(ts)
                    count = None

                    # 遍历化学式列（奇数列）
                    for col_idx in range(1, len(df.columns), 2):
                        if row[df.columns[col_idx]] == chemical:
                            count = row[df.columns[col_idx + 1]]  # 对应数量列
                            break

                    if ts not in timestep_data:
                        timestep_data[ts] = {}
                    timestep_data[ts][current_file_name] = count

            except Exception as e:
                messagebox.showerror("文件错误", f"读取{filename}失败：{str(e)}")
                return

        # 整理结果
        sorted_ts = sorted(all_timesteps)
        result_rows = []
        for ts in sorted_ts:
            row = {"timestep": ts}
            for file_name in file_names:
                row[file_name] = timestep_data.get(ts, {}).get(file_name, None)
            result_rows.append(row)

        # 保存结果
        result_df = pd.DataFrame(result_rows)
        result_df = result_df[["timestep"] + file_names]
        output_path = os.path.join(species_dir, f"{chemical}.xlsx")

        try:
            result_df.to_excel(output_path, index=False)
            messagebox.showinfo("完成", f"分析完成！结果文件已保存至：\n{output_path}")
            self.status.set(f"化学式{chemical}分析完成")
        except Exception as e:
            messagebox.showerror("保存失败", f"结果文件保存失败：{str(e)}")

    def process_statistics(self):
        """功能：物种数和分子数统计"""
        root_dir = self.target_folder.get()
        if not root_dir:
            messagebox.showwarning("提示", "请先选择目标文件夹！")
            return

        species_dir = os.path.join(root_dir, "物种分析")
        if not os.path.exists(species_dir):
            messagebox.showwarning("提示", "未找到'物种分析'文件夹，请先运行初始分析！")
            return

        # 仅处理原始转换生成的文件（子文件夹名.xlsx）
        subfolders = [f for f in os.listdir(root_dir)
                      if os.path.isdir(os.path.join(root_dir, f))]
        original_files = [f"{subfolder}.xlsx" for subfolder in subfolders]
        xlsx_files = [f for f in os.listdir(species_dir)
                      if f.endswith(".xlsx") and f in original_files]

        if not xlsx_files:
            messagebox.showwarning("提示", "未找到原始转换生成的xlsx文件！")
            return

        # 初始化统计字典
        species_count = {}  # 物种数统计：{timestep: {文件名: count}}
        molecule_count = {}  # 分子数统计：{timestep: {文件名: sum}}
        all_timesteps = set()
        file_names = [os.path.splitext(f)[0] for f in xlsx_files]  # 去.xlsx后缀

        # 遍历文件统计数据
        for filename in xlsx_files:
            file_path = os.path.join(species_dir, filename)
            try:
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    ts = row["时间步"]
                    all_timesteps.add(ts)

                    # 统计物种数（非空化学式列的数量）
                    chem_cols = [col for col in df.columns if col.startswith("化学式")]
                    current_species = sum(1 for col in chem_cols if pd.notna(row[col]))

                    # 统计分子数（数量列的数值和）
                    num_cols = [col for col in df.columns if col.startswith("数量")]
                    current_molecules = sum(row[col] for col in num_cols if pd.notna(row[col]))

                    # 记录数据
                    if ts not in species_count:
                        species_count[ts] = {}
                    species_count[ts][filename] = current_species

                    if ts not in molecule_count:
                        molecule_count[ts] = {}
                    molecule_count[ts][filename] = current_molecules

            except Exception as e:
                messagebox.showerror("文件错误", f"读取{filename}失败：{str(e)}")
                return

        # 整理物种数数据
        species_rows = []
        for ts in sorted(all_timesteps):
            row = {"timestep": ts}
            for file in xlsx_files:
                row[os.path.splitext(file)[0]] = species_count.get(ts, {}).get(file, 0)
            species_rows.append(row)
        species_df = pd.DataFrame(species_rows)
        species_df = species_df[["timestep"] + file_names]

        # 整理分子数数据
        molecule_rows = []
        for ts in sorted(all_timesteps):
            row = {"timestep": ts}
            for file in xlsx_files:
                row[os.path.splitext(file)[0]] = molecule_count.get(ts, {}).get(file, 0)
            molecule_rows.append(row)
        molecule_df = pd.DataFrame(molecule_rows)
        molecule_df = molecule_df[["timestep"] + file_names]

        # 保存双工作表结果
        output_path = os.path.join(species_dir, "物种数和分子数统计.xlsx")
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                species_df.to_excel(writer, sheet_name="物种数", index=False)
                molecule_df.to_excel(writer, sheet_name="分子数", index=False)

            messagebox.showinfo("完成", f"统计完成！结果文件已保存至：\n{output_path}")
            self.status.set("物种数和分子数统计完成")
        except Exception as e:
            messagebox.showerror("保存失败", f"结果文件保存失败：{str(e)}")

    def process_reactants(self):
        """功能：反应物统计"""
        root_dir = self.target_folder.get()
        if not root_dir:
            messagebox.showwarning("提示", "请先选择目标文件夹！")
            return

        species_dir = os.path.join(root_dir, "物种分析")
        if not os.path.exists(species_dir):
            messagebox.showwarning("提示", "未找到'物种分析'文件夹，请先运行初始分析！")
            return

        # 仅处理原始转换生成的文件（子文件夹名.xlsx）
        subfolders = [f for f in os.listdir(root_dir)
                      if os.path.isdir(os.path.join(root_dir, f))]
        original_files = [f"{subfolder}.xlsx" for subfolder in subfolders]
        xlsx_files = [f for f in os.listdir(species_dir)
                      if f.endswith(".xlsx") and f in original_files]

        if not xlsx_files:
            messagebox.showwarning("提示", "未找到原始转换生成的xlsx文件！")
            return

        # 收集所有化学式（来自每个文件的最后一行）
        all_chemicals = set()
        last_row_data = {}  # 存储每个文件的最后一行数据 {文件名: 最后一行数据}

        for filename in xlsx_files:
            file_path = os.path.join(species_dir, filename)
            try:
                df = pd.read_excel(file_path)
                if len(df) == 0:
                    continue

                last_row = df.iloc[-1]  # 获取最后一行
                last_row_data[filename] = last_row

                # 收集化学式
                for col in df.columns:
                    if col.startswith("化学式") and pd.notna(last_row[col]):
                        all_chemicals.add(last_row[col])
            except Exception as e:
                messagebox.showerror("文件错误", f"读取{filename}失败：{str(e)}")
                return

        if not all_chemicals:
            messagebox.showinfo("提示", "未找到任何化学式！")
            return

        # 创建输出文件
        output_path = os.path.join(species_dir, "反应物统计.xlsx")

        try:
            # 存储化学式数据和总数量
            chemical_data = []

            # 处理每个化学式
            for chem in all_chemicals:
                # 创建安全的工作表名称
                clean_chem = re.sub(r'[\\/*?\[\]:]', '', chem)
                sheet_name = clean_chem[:31]
                if not sheet_name.strip():
                    sheet_name = "chemical_" + str(len(chemical_data) + 1)

                # 创建数据框架
                data = {"timestep": []}

                # 为每个文件添加列
                for filename in xlsx_files:
                    short_name = os.path.splitext(filename)[0]
                    data[short_name] = []

                # 遍历所有文件
                for filename in xlsx_files:
                    file_path = os.path.join(species_dir, filename)
                    try:
                        df = pd.read_excel(file_path)
                        short_name = os.path.splitext(filename)[0]

                        # 为每个时间步添加一行
                        for ts in df["时间步"].unique():
                            if ts not in data["timestep"]:
                                data["timestep"].append(ts)
                                # 初始化所有列为0
                                for col in data:
                                    if col != "timestep" and col != short_name:
                                        if len(data[col]) < len(data["timestep"]):
                                            data[col].append(0)

                            # 查找当前时间步的行
                            row_idx = data["timestep"].index(ts)

                            # 确保所有列都有足够的数据
                            for col in data:
                                if col != "timestep" and len(data[col]) <= row_idx:
                                    data[col].append(0)

                            # 获取当前时间步的数据
                            ts_data = df[df["时间步"] == ts].iloc[0]

                            # 查找化学式的数量
                            chem_found = False
                            for i in range(1, len(df.columns), 2):
                                if df.columns[i].startswith("化学式") and ts_data[df.columns[i]] == chem:
                                    count = ts_data[df.columns[i + 1]]
                                    data[short_name][row_idx] = count
                                    chem_found = True
                                    break

                            # 如果未找到，设置为0
                            if not chem_found:
                                data[short_name][row_idx] = 0

                    except Exception as e:
                        messagebox.showerror("处理错误", f"处理文件{filename}时出错：{str(e)}")
                        return

                # 创建DataFrame
                df_result = pd.DataFrame(data)
                df_result.sort_values(by="timestep", inplace=True)

                # 计算整个工作表中该化学式数量的总和
                total_count = 0
                for col in df_result.columns:
                    if col != "timestep":
                        total_count += df_result[col].sum()

                # 存储化学式数据
                chemical_data.append({
                    "chem": chem,
                    "sheet_name": sheet_name,
                    "df_result": df_result,
                    "total_count": total_count
                })

            # 按总数量从大到小排序
            chemical_data.sort(key=lambda x: x["total_count"], reverse=True)

            # 创建Excel写入对象
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 写入每个化学式的工作表
                for chem_data in chemical_data:
                    chem = chem_data["chem"]
                    sheet_name = chem_data["sheet_name"]
                    df_result = chem_data["df_result"]
                    total_count = chem_data["total_count"]

                    # 创建新的数据框架，包含化学式信息和总数量
                    summary_df = pd.DataFrame({
                        "化学式": [chem],
                        "总数量": [total_count]
                    })

                    # 写入工作表
                    # 先写入化学式信息和总数量
                    summary_df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # 然后写入详细数据（从第三行开始）
                    df_result.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)

            messagebox.showinfo("完成", f"反应物统计完成！结果已保存至：\n{output_path}")
            self.status.set("反应物统计完成")

        except Exception as e:
            messagebox.showerror("保存失败", f"结果文件保存失败：{str(e)}")


if __name__ == "__main__":
    root = Tk()
    app = SpeciesAnalyzer(root)
    root.mainloop()