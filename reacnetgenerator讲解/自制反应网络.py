import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import networkx as nx
import random
from pyvis.network import Network
import openbabel as ob


# 定义读取文件的函数
def read_reaction_file():
    filepath = filedialog.askopenfilename(filetypes=[("Reaction files", "*.reaction")])
    if filepath:
        process_reaction_file(filepath)


# 定义处理反应文件的函数
def process_reaction_file(filepath):
    # 读取反应文件并分列
    reaction_data = pd.read_csv(filepath, header=None, delimiter=' ', names=['Frequency', 'Reaction'])
    reaction_data[['Reactant', 'Product']] = reaction_data['Reaction'].str.split("->", expand=True)

    # 只保留频次超过10的反应
    reaction_data = reaction_data[reaction_data['Frequency'] > 10]

    # 创建反应网络
    G = nx.DiGraph()

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
    intermediate_smiles = {}
    for intermediate in intermediates:
        # 尝试使用 RDKit 处理分子
        mol = Chem.MolFromSmiles(intermediate)
        if mol is not None:
            intermediate_smiles[intermediate] = intermediate
            intermediate_formulae[intermediate] = Chem.rdMolDescriptors.CalcMolFormula(mol)
        else:
            # 如果无法转换为分子，则将第二列留空
            intermediate_formulae[intermediate] = ""

    # 将节点信息写入文件
    with open('n.txt', 'w') as node_file:
        for intermediate, formula in intermediate_formulae.items():
            # 检查分子公式是否为空，如果为空则手动为其赋一个空字符串
            if formula:
                node_file.write(f"{intermediate}\t{formula}\n")
            else:
                node_file.write(f"{intermediate}\t\n")

    print("Node information written to n.txt")

    # 创建Pyvis网络对象
    net = Network(notebook=True)

    # 添加节点和边到Pyvis网络
    with open('n.txt', 'r') as node_file:
        for line in node_file:
            line = line.strip().split('\t')
            intermediate = line[0]
            label = line[1] if len(line) > 1 else ''  # 从文件中读取标签，如果没有则使用空字符串
            color = random.choice(
                ['lightcoral', 'lightsalmon', 'lightgoldenrodyellow', 'lightgreen', 'lightseagreen', 'lightblue',
                 'mediumpurple'])
            node_size = 10 + node_size_increment.get()  # 节点大小增量
            # 如果标签为空，则使用 Open Babel 转换 SMILES 为分子式
            if not label:
                obConversion = ob.OBConversion()
                obConversion.SetInAndOutFormats("smi", "can")
                mol = ob.OBMol()
                obConversion.ReadString(mol, intermediate)
                label = mol.GetFormula()

            net.add_node(intermediate, title=label, label=label, color=color, size=node_size)

    for u, v, d in G.edges(data=True):
        frequency = d['frequency']
        if frequency > 10:
            line_width = 1.0 + line_width_increment.get()  # 线条粗细增量
            if frequency > 100:
                line_width += 1.0
            if frequency > 1000:
                line_width += 1.0
            net.add_edge(u, v, title=f"Frequency: {frequency}", width=line_width)

    # 显示Pyvis网络
    net.show_buttons(filter_=['physics'])
    net.show("reaction_network.html")

    # 进行聚类分析
    # 假设进行了聚类分析并获得了结果，这里仅作演示
    clustering_result = "Cluster 1: A, B, C\nCluster 2: D, E, F"

    # 输出聚类分析的结果到文本框
    text_output.delete('1.0', tk.END)  # 清空文本框
    text_output.insert(tk.END, clustering_result)


# 创建主窗口
root = tk.Tk()
root.title("Reaction Network Generator")

# 添加按钮
btn_browse = tk.Button(root, text="Browse Reaction File", command=read_reaction_file)
btn_browse.pack(pady=20)

# 添加节点大小增量滑块
node_size_increment = tk.DoubleVar()
node_size_increment.set(0.0)
node_size_label = tk.Label(root, text="Node Size Increment:")
node_size_label.pack()
node_size_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=node_size_increment)
node_size_slider.pack()

# 添加线条粗细增量滑块
line_width_increment = tk.DoubleVar()
line_width_increment.set(0.0)
line_width_label = tk.Label(root, text="Line Width Increment:")
line_width_label.pack()
line_width_slider = tk.Scale(root, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                             variable=line_width_increment)
line_width_slider.pack()

# 添加文本框
text_output = tk.Text(root, height=10, width=50)
text_output.pack(pady=20)

# 运行主循环
root.mainloop()
