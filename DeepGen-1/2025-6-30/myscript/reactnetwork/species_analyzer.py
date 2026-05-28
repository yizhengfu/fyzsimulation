import os
import shutil
import re
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeciesAnalyzer:
    def __init__(self, target_folder=None):
        # 如果没有指定目标文件夹，则使用当前目录
        self.target_folder = target_folder if target_folder else os.getcwd()
        logger.info(f"目标文件夹设置为: {self.target_folder}")
        
        # 创建物种分析目录
        self.species_dir = os.path.join(self.target_folder, "species_analysis")
        os.makedirs(self.species_dir, exist_ok=True)
        logger.info(f"创建分析目录: {self.species_dir}")
        
        # 按顺序执行所有分析步骤
        self.process_files()
        self.process_statistics()
        self.process_reactants()
        logger.info("所有分析步骤已完成")

    def process_files(self):
        """核心功能：原始文件转换（.species → .txt/.xlsx）"""
        logger.info("开始处理文件...")
        processed = 0
        errors = []

        try:
            # 遍历根目录下的所有子文件夹，排除新创建的species_analysis目录
            subfolders = [f for f in os.listdir(self.target_folder)
                          if os.path.isdir(os.path.join(self.target_folder, f)) 
                          and f != os.path.basename(self.species_dir)]

            for subfolder in subfolders:
                subfolder_path = os.path.join(self.target_folder, subfolder)
                species_files = [f for f in os.listdir(subfolder_path)
                                 if f.endswith(".species")]
                if not species_files:
                    logger.warning(f"子文件夹 '{subfolder}' 无.species文件")
                    errors.append(f"子文件夹 '{subfolder}' 无.species文件")
                    continue

                # 处理第一个.species文件（假设唯一）
                src_file = os.path.join(subfolder_path, species_files[0])
                txt_dest = os.path.join(self.species_dir, f"{subfolder}.txt")
                xlsx_dest = os.path.join(self.species_dir, f"{subfolder}.xlsx")

                try:
                    # 复制并重命名为.txt
                    shutil.copy2(src_file, txt_dest)

                    # 解析文件内容
                    with open(txt_dest, 'r', encoding='utf-8') as f:
                        content = f.read()

                    timestep_data = self.parse_timestep_data(content)
                    if not timestep_data:
                        logger.warning(f"{subfolder}.txt 无有效时间步数据")
                        errors.append(f"{subfolder}.txt 无有效时间步数据")
                        continue

                    # 计算最大结构对数（确定列数）
                    max_pairs = max(len(pairs) for pairs in timestep_data.values()) if timestep_data else 0
                    if max_pairs == 0:
                        logger.warning(f"{subfolder}.txt 无有效结构-数量对")
                        errors.append(f"{subfolder}.txt 无有效结构-数量对")
                        continue

                    # 生成Excel列名
                    columns = ["timestep"]
                    for i in range(1, max_pairs + 1):
                        columns.append(f"chemical_formula_{i}")
                        columns.append(f"count_{i}")

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
                    logger.info(f"已处理 {processed} 个文件: {subfolder}")

                except Exception as e:
                    logger.error(f"子文件夹 '{subfolder}' 处理失败: {str(e)}")
                    errors.append(f"子文件夹 '{subfolder}' 处理失败：{str(e)}")

            # 显示处理结果
            logger.info(f"文件处理完成! 成功: {processed}, 失败: {len(errors)}")
            if errors:
                logger.warning("处理异常文件列表:\n" + "\n".join(errors))

        except Exception as e:
            logger.error(f"文件处理过程中发生严重错误: {str(e)}")

    def parse_timestep_data(self, content):
        """
        解析.species文件内容，提取时间步和结构数据
        使用改进的SMILES格式解析逻辑
        """
        timestep_dict = {}
        # 匹配时间步及其内容
        timestep_pattern = re.compile(r'Timestep (\d+):(.*?)(?=Timestep \d+:|$)', re.DOTALL)

        # 匹配SMILES分子式和数量的对
        structure_pattern = re.compile(r'([^\s]+?)\s+(\d+)(?=\s|$)')

        timesteps = timestep_pattern.findall(content)
        for ts_num, ts_content in timesteps:
            ts_num = int(ts_num)
            structures = []

            # 使用正则表达式查找所有匹配的分子式-数量对
            matches = structure_pattern.findall(ts_content)

            # 处理匹配结果
            for chem, count in matches:
                # 检查分子式是否有效
                if '[' in chem or any(c.isalpha() for c in chem):
                    structures.append((chem, int(count)))

            if structures:
                timestep_dict[ts_num] = structures

        return timestep_dict

    def process_statistics(self):
        """功能：物种数和分子数统计"""
        logger.info("开始物种数和分子数统计...")
        
        # 仅处理原始转换生成的文件（子文件夹名.xlsx）
        subfolders = [f for f in os.listdir(self.target_folder)
                      if os.path.isdir(os.path.join(self.target_folder, f)) 
                      and f != os.path.basename(self.species_dir)]
        original_files = [f"{subfolder}.xlsx" for subfolder in subfolders]
        xlsx_files = [f for f in os.listdir(self.species_dir)
                      if f.endswith(".xlsx") and f in original_files]

        if not xlsx_files:
            logger.warning("未找到原始转换生成的xlsx文件!")
            return

        # 初始化统计字典
        species_count = {}  # 物种数统计：{timestep: {文件名: count}}
        molecule_count = {}  # 分子数统计：{timestep: {文件名: sum}}
        all_timesteps = set()
        file_names = [os.path.splitext(f)[0] for f in xlsx_files]  # 去.xlsx后缀

        # 遍历文件统计数据
        for filename in xlsx_files:
            file_path = os.path.join(self.species_dir, filename)
            try:
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    ts = row["timestep"]
                    all_timesteps.add(ts)

                    # 统计物种数（非空化学式列的数量）
                    chem_cols = [col for col in df.columns if col.startswith("chemical_formula_")]
                    current_species = sum(1 for col in chem_cols if pd.notna(row[col]))

                    # 统计分子数（数量列的数值和）
                    num_cols = [col for col in df.columns if col.startswith("count_")]
                    current_molecules = sum(row[col] for col in num_cols if pd.notna(row[col]))

                    # 记录数据
                    if ts not in species_count:
                        species_count[ts] = {}
                    species_count[ts][filename] = current_species

                    if ts not in molecule_count:
                        molecule_count[ts] = {}
                    molecule_count[ts][filename] = current_molecules

            except Exception as e:
                logger.error(f"读取{filename}失败: {str(e)}")
                continue

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
        output_path = os.path.join(self.species_dir, "species_and_molecule_stats.xlsx")
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 使用英文工作表名称
                species_df.to_excel(writer, sheet_name="Number of species", index=False)
                molecule_df.to_excel(writer, sheet_name="number of molecules", index=False)

            logger.info(f"统计完成! 结果文件: {output_path}")
        except Exception as e:
            logger.error(f"结果文件保存失败: {str(e)}")

    def process_reactants(self):
        """功能：反应物统计"""
        logger.info("开始反应物统计...")
        
        # 仅处理原始转换生成的文件（子文件夹名.xlsx）
        subfolders = [f for f in os.listdir(self.target_folder)
                      if os.path.isdir(os.path.join(self.target_folder, f)) 
                      and f != os.path.basename(self.species_dir)]
        original_files = [f"{subfolder}.xlsx" for subfolder in subfolders]
        xlsx_files = [f for f in os.listdir(self.species_dir)
                      if f.endswith(".xlsx") and f in original_files]

        if not xlsx_files:
            logger.warning("未找到原始转换生成的xlsx文件!")
            return

        # 收集所有化学式（来自每个文件的最后一行）
        all_chemicals = set()
        last_row_data = {}  # 存储每个文件的最后一行数据 {文件名: 最后一行数据}

        for filename in xlsx_files:
            file_path = os.path.join(self.species_dir, filename)
            try:
                df = pd.read_excel(file_path)
                if len(df) == 0:
                    continue

                last_row = df.iloc[-1]  # 获取最后一行
                last_row_data[filename] = last_row

                # 收集化学式
                for col in df.columns:
                    if col.startswith("chemical_formula_") and pd.notna(last_row[col]):
                        all_chemicals.add(last_row[col])
            except Exception as e:
                logger.error(f"读取{filename}失败: {str(e)}")
                continue

        if not all_chemicals:
            logger.warning("未找到任何化学式!")
            return

        # 创建输出文件
        output_path = os.path.join(self.species_dir, "reactants_stats.xlsx")
        logger.info(f"发现 {len(all_chemicals)} 个化学式, 正在生成报告...")

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
                    file_path = os.path.join(self.species_dir, filename)
                    try:
                        df = pd.read_excel(file_path)
                        short_name = os.path.splitext(filename)[0]

                        # 为每个时间步添加一行
                        for ts in df["timestep"].unique():
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
                            ts_data = df[df["timestep"] == ts].iloc[0]

                            # 查找化学式的数量
                            chem_found = False
                            for i in range(1, len(df.columns), 2):
                                col_name = df.columns[i]
                                if col_name.startswith("chemical_formula_") and ts_data[col_name] == chem:
                                    count_col = df.columns[i+1]
                                    if count_col.startswith("count_"):
                                        count = ts_data[count_col]
                                        data[short_name][row_idx] = count
                                        chem_found = True
                                        break

                            # 如果未找到，设置为0
                            if not chem_found:
                                data[short_name][row_idx] = 0

                    except Exception as e:
                        logger.error(f"处理文件{filename}时出错: {str(e)}")
                        continue

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
                        "Chemical Formula": [chem],
                        "Total Count": [total_count]
                    })

                    # 写入工作表
                    # 先写入化学式信息和总数量
                    summary_df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # 然后写入详细数据（从第三行开始）
                    df_result.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)

            logger.info(f"反应物统计完成! 结果文件: {output_path}")

        except Exception as e:
            logger.error(f"结果文件保存失败: {str(e)}")


if __name__ == "__main__":
    # 获取目标文件夹（如果有命令行参数）
    import sys
    target_folder = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 执行分析
    analyzer = SpeciesAnalyzer(target_folder)