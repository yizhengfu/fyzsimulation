# projects — 分子动力学仿真项目索引

fyzsimulation 中所有 LAMMPS 仿真项目的分类索引。每个目录下有详细 README。

---

## 4-8 — MOF 膜气体扩散

MOF/石墨烯/ZIF/聚合物复合膜中 CH₄/H₂O 混合气体扩散模拟。
→ [4-8/README.md](4-8/README.md)

**子项目**: 0v1~1v9（层间距系列）、1v1onelayer（单层膜）、Graphene（石墨烯膜）、KA 系列、PC 系列（聚合物复合）、Zif、4-15（多种材料对比）

## gap — GAP 反应力场

基于 Gaussian Approximation Potential（GAP）的反应力场训练数据。
- **数据量**: 1.9GB, ~2万个文件
- **内容**: 不同能量范围的构型（0/100/300/500 kcal/mol），ReaxFF 力场文件
- **用途**: 机器学习势函数训练

## 扩散模拟 — MOF 扩散（旧版本）

旧版 MOF 膜扩散模拟，结构与 `4-8/` 类似但为早期版本。
- 包含 `0v1~1v9` 等子目录
- **注意**: `4-8/` 是更新版本，可能存在重复

## research — 研究项目集

多个独立研究案例的汇总：
- **纳米压痕**（Cu 单晶压痕）
- **剪切作用**（Deform vs Velocity 两种方法对比, Ni 体系）
- **切削/磨削**（SiC 切削, 高熵合金磨削）
- **单轴压缩**（应力应变曲线+弹性模量）
- **粘度计算**（RNEMD/Green-Kubo 方法）
- **椭圆振动**（SiC 和 Fe 的椭圆振动辅助加工）
- **热导率**（NEMD/EMD 五种方法）
- **循环压痕**

## poly — 聚合物拉伸

聚乙烯（Polyethylene）在不同应变率下的拉伸模拟。
- **应变率**: 5e-5 ~ 5e-9 范围，300K 和 400K
- 包含应力应变数据

## shear — 剪切模拟

不同剪切速率下的剪切行为，含无定形碳（xlink）和聚乙烯。

## viscosity — 粘度计算

GK（Green-Kubo）/ NEMD（非平衡）/ EMD（Einstein）/ Wall 多种粘度计算方法。
- 包含 Ar、Cu、NaCl、SiC 等多种体系
- 含表面张力模拟（液态-气相界面）
- 含 DPD 粗粒化模拟

## tension — 拉伸

Ge（锗）和石墨烯的拉伸模拟。

## 力学性能 — LAMMPS 输入文件

通用力学性能计算的 LAMMPS 输入文件合集（拉伸/剪切/压缩/Tg/平衡等）。
存放在 projects/in文件 中的才是最近更新的版本。

## crosslink — 交联

环氧树脂（epoxy）交联反应的 LAMMPS+Python 脚本。
- 含 `SU8pcff.data`（交联体系）、`improper_add_type.py`（类型修正脚本）

## friction — 摩擦

摩擦/磨损模拟的 LAMMPS 输入文件。

## impact — 冲击

冲击动力学模拟。
- 含 Bullet（弹丸）、Graphene（石墨烯靶材）等模型

## clusrer — 集群脚本

Slurm 集群提交脚本。

## 反应力场后处理 — ReaxFF 分析

ReaxFF 反应力场结果后处理 Python 脚本：
- **主要产物.py** — 统计主要反应产物
- **反应时间.py** — 反应时间序列分析
- **物种数分子数.py** — 物种演化统计
- **成键可视化/** — 成键分析

## 后处理 — LAMMPS 后处理

通用 LAMMPS 后处理脚本：
- in-dump.txt（dump 文件处理）, in-rdf.txt（RDF 分析）
- 统计产物.ini/.txt（产物统计）

## 扩散 — 扩散模拟 LAMMPS 输入

不同材料体系扩散模拟的 LAMMPS 输入文件（in.Diff-*.txt）。

## 玻璃碳 — 玻璃碳 ReaxFF

玻璃碳（glassy carbon）在高温下的分解模拟（3500K）。

## 蒸发 — 蒸发模拟

LAMMPS 蒸发/冷凝模拟，含溶剂蒸发过程视频。

## usall — 通用输入文件

通用 LAMMPS 输入模板（拉伸/剪切/平衡/Tg/循环加载等）。

## in文件 — 最新版 LAMMPS 输入

更新版的通用 LAMMPS 输入文件（平衡/拉伸/剪切/循环加载等），和 `力学性能/` 内容类似但是更新的版本。

## pdf — 参考资料

PDF/DOCX 参考资料（LAMMPS 教程、扩散膜心得、摩擦/拉伸等）。
