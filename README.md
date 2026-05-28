# fyzsimulation — 材料分子动力学仿真工作台

LAMMPS 分子动力学模拟 + ReaxFF 反应力场 + DeepMD 机器学习势函数的工作目录。

## 目录结构

```
fyzsimulation/
├── ML/               # 机器学习相关脚本（DP-GEN、sklearn 回归模型）
├── Python/           # Python 学习练习
├── projects/         # 仿真项目（核心数据）
│   ├── 4-8/          # MOF/石墨烯/ZIF 膜气体扩散模拟
│   ├── gap/          # GAP 反应力场训练数据
│   ├── poly/         # 聚乙烯拉伸模拟
│   ├── shear/        # 剪切模拟
│   ├── viscosity/    # 粘度/表面张力计算
│   ├── research/     # 研究案例集（纳米压痕、切削、冲击等）
│   └── ...           # 更多子项目
├── scripts/          # 后处理/分析脚本
├── tools/            # 第三方工具（msi2lmp, MS Perl 脚本等）
├── workflows/        # 自动化工作流（待补充）
├── .vscode/          # VS Code 配置
└── .gitignore
```

## 各文件夹速查

| 目录 | 文件数 | 大小 | 说明 |
|------|--------|------|------|
| `projects/` | ~20000+ | 6.8GB | **所有 LAMMPS 仿真项目**（核心数据）|
| `scripts/` | 26 | 134MB | Python 后处理和 ReacNetGenerator 工具 |
| `tools/` | 73 | 29MB | msi2lmp 转换器、MS Perl 脚本、力场文件 |
| `ML/` | 5 | 88K | DP-GEN 和机器学习 GUI 脚本 |
| `Python/` | 3 | 16K | 线性回归学习练习 |
| `workflows/` | 0 | 0 | 自动化工作流（空） |

## 使用提示

- 各子目录下有 `README.md` 说明详情
- `projects/README.md` 是项目总索引
- 仿真输出文件（`.lammpstrj`, `.data`, `.log` 等）被 `.gitignore` 忽略，不上传 GitHub
- **GitHub 仓库仅保留输入文件、脚本和文档**
