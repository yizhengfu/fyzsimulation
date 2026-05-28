#!/usr/bin/env python3
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import networkx as nx
import random
from pyvis.network import Network
import openbabel as ob
import os
import glob
import sys
import argparse

def get_molecular_formula(smiles):
    """获取分子式，使用RDKit或OpenBabel"""
    mol = Chem.MolFromSmiles(smiles)
    if mol is not None:
        try:
            return rdMolDescriptors.CalcMolFormula(mol)
        except:
            pass
    
    # 如果无法转换为分子，则尝试使用 Open Babel
    try:
        obConversion = ob.OBConversion()
        obConversion.SetInAndOutFormats("smi", "can")
        mol = ob.OBMol()
        obConversion.ReadString(mol, smiles)
        return mol.GetFormula()
    except:
        return ""

def process_reaction_file(filepath, target_smiles=None, node_size_inc=0.0, line_width_inc=0.0):
    """处理单个反应文件"""
    print(f"处理文件: {os.path.basename(filepath)}")
    
    # 读取反应文件并分列
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  错误: 无法读取文件 - {str(e)}")
        return False
    
    # 创建反应网络
    G = nx.DiGraph()
    processed_lines = []
    
    # 处理每行反应
    for line in lines:
        parts = line.strip().split(' ', 1)
        if len(parts) < 2:
            continue

        try:
            frequency = int(parts[0])
        except ValueError:
            continue

        reaction = parts[1]

        if '->' in reaction:
            reactant, product = reaction.split('->')
            reactant = reactant.strip()
            product = product.strip()

            # 严格匹配SMILES
            if target_smiles:
                if target_smiles != reactant and target_smiles != product:
                    continue

            if frequency > 10:
                processed_lines.append((frequency, reactant, product))

    # 如果没有匹配的反应
    if not processed_lines:
        print(f"  警告: 没有找到符合条件的反应")
        return False

    # 处理反应数据
    reaction_data = pd.DataFrame(processed_lines, columns=['Frequency', 'Reactant', 'Product'])

    # 添加节点（反应物和产物）
    for index, row in reaction_data.iterrows():
        reactant = row['Reactant']
        product = row['Product']
        G.add_node(reactant)
        G.add_node(product)
        G.add_edge(reactant, product, frequency=row['Frequency'])

    # 转换为分子指纹
    intermediates = list(set(reaction_data['Reactant']) | set(reaction_data['Product']))
    intermediate_formulae = {}
    for intermediate in intermediates:
        intermediate_formulae[intermediate] = get_molecular_formula(intermediate)

    # 创建Pyvis网络对象
    net = Network(notebook=True, directed=True, height="800px", width="100%")

    # 添加节点到Pyvis网络
    for intermediate in intermediates:
        label = intermediate_formulae.get(intermediate, '')
        color = random.choice(['lightcoral', 'lightsalmon', 'lightgoldenrodyellow',
                               'lightgreen', 'lightseagreen', 'lightblue', 'mediumpurple'])
        node_size = 20 + node_size_inc  # 节点大小增量
        net.add_node(intermediate, title=label, label=label, color=color, size=node_size)

    # 添加边到Pyvis网络
    for u, v, d in G.edges(data=True):
        frequency = d['frequency']
        if frequency > 10:
            line_width = 1.0 + line_width_inc  # 线条粗细增量
            if frequency > 100:
                line_width += 1.0
            if frequency > 1000:
                line_width += 1.0
            net.add_edge(u, v, title=f"Frequency: {frequency}", width=line_width)

    # 生成输出文件名
    output_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_file = os.path.join(output_dir, f"{base_name}_network.html")
    
    # 保存网络
    net.save_graph(output_file)
    
    # 输出网络信息
    print(f"  生成网络文件: {output_file}")
    print(f"  节点数: {G.number_of_nodes()}")
    print(f"  边数: {G.number_of_edges()}")
    return True

def process_directory(target_dir, target_smiles=None, node_size_inc=0.0, line_width_inc=0.0):
    """处理目录中的所有.reaction文件"""
    print(f"扫描目录: {target_dir}")
    reaction_files = glob.glob(os.path.join(target_dir, "**", "*.reaction"), recursive=True)
    
    if not reaction_files:
        print("未找到任何.reaction文件")
        return
    
    print(f"找到 {len(reaction_files)} 个.reaction文件")
    print("开始处理...")
    print("-" * 50)
    
    success_count = 0
    for i, filepath in enumerate(reaction_files, 1):
        print(f"处理文件 {i}/{len(reaction_files)}")
        if process_reaction_file(filepath, target_smiles, node_size_inc, line_width_inc):
            success_count += 1
        print("-" * 50)
    
    print(f"处理完成! 成功处理 {success_count}/{len(reaction_files)} 个文件")

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="化学反应网络生成器(命令行版)")
    parser.add_argument("-d", "--directory", default=".", 
                       help="要扫描的目录(默认为当前目录)")
    parser.add_argument("-s", "--smiles", 
                       help="筛选特定的SMILES字符串")
    parser.add_argument("--node_size", type=float, default=0.0,
                       help="节点大小增量(默认为0.0)")
    parser.add_argument("--line_width", type=float, default=0.0,
                       help="线条粗细增量(默认为0.0)")
    
    args = parser.parse_args()
    
    # 显示参数信息
    print("=" * 50)
    print("化学反应网络生成器(命令行版)")
    print("=" * 50)
    print(f"扫描目录: {args.directory}")
    if args.smiles:
        print(f"筛选SMILES: {args.smiles}")
    print(f"节点大小增量: {args.node_size}")
    print(f"线条粗细增量: {args.line_width}")
    print("=" * 50)
    
    # 处理目录
    process_directory(
        args.directory,
        target_smiles=args.smiles,
        node_size_inc=args.node_size,
        line_width_inc=args.line_width
    )

if __name__ == "__main__":
    main()