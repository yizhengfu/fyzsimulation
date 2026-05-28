# fyzsimulation — 材料仿真脚本工具集

smaster 服务器 `/data/run/myscript` 目录下的脚本和配置文件集合。涵盖了从第一性原理计算（CP2K）、深度学习势函数训练（DeepMD/DP-GEN）、分子动力学（LAMMPS）到反应网络分析（ReacNetGenerator）的完整计算工作流。

---

## 目录结构

```
myscript/
├── cp2k/                      # CP2K 输入文件与生成脚本
├── deepgen/                   # DP-GEN 深度学习势函数生成
├── deepmd_kit/                # DeepMD-kit 训练与测试
│   ├── aimd/                  # AIMD 数据生成
│   └── lammps/                # LAMMPS 配合 DeepMD 的输入
├── jupyter/                   # Jupyter 环境配置
├── lammps/                    # LAMMPS 输入文件
├── reactnetwork/              # ReacNetGenerator 反应网络分析
│   └── windows/               # Windows 版 GUI 工具
├── syncthing/                 # Syncthing 多用户同步配置
├── energy.py                  # 能量/活化能分析绘图工具
├── cp2kcpu.sh                 # CP2K CPU 批量提交脚本 (Slurm)
├── cp2kgpu.sh                 # CP2K GPU 批量提交脚本 (Slurm)
├── cp2k_speed_test.sh         # CP2K CPU/GPU 性能对比测试
├── lmp-cpu+deemd.sh           # LAMMPS CPU+DeepMD 批量提交
├── lmp-gpu-kokkos+deepmd.sh   # LAMMPS GPU+Kokkos+DeepMD 批量提交
├── lmp_speed_test.sh          # LAMMPS CPU/GPU 性能对比测试
├── useradd.sh                 # 创建集群用户
├── .gitignore                 # Git 忽略规则
└── README.md                  # 本文件
```

---

## 各文件/目录功能详解

### 📂 cp2k/ — CP2K 输入文件与生成

| 文件 | 功能 | 说明 |
|------|------|------|
| `Al_H2O_GAS.inp` | CP2K 输入文件 | Al-H₂O 气相体系的 MD 模拟输入，使用 Multiwfn 生成 |
| `cp2k_AIMD.bat` | Windows 批处理 | 遍历 `.cif` 文件 → Multiwfn 生成 CP2K 输入 → 添加 NVT (Nose-Hoover) MD 参数块（1000步, 298.15K） |
| `cp2k_Dpgen.bat` | Windows 批处理 | 遍历 `.cif` 文件 → Multiwfn 生成 CP2K 输入 → 用于 DP-GEN 的单点能/力计算 |
| `cp2k_OS.bat` | Windows 批处理 | 遍历 `.cif` 文件 → Multiwfn 生成 CP2K 输入 → 能带结构/态密度计算（k-point 3×3×3） |

三个 `.bat` 文件都依赖 **Multiwfn** 从 `.cif` 结构文件生成 CP2K 输入，再自动修改 `PRINT_LEVEL` 和收敛设置。

---

### 📂 deepgen/ — DP-GEN 深度学习势函数生成

| 文件 | 功能 | 说明 |
|------|------|------|
| `CP2K-DP.py` | Python 策略生成器 | 核心脚本：读取 CP2K AIMD 输出 → 用 `dpdata` 转换为 DeepMD 训练数据格式。支持 Tkinter 图形界面 + 多线程处理。目前 `dpdata` 的 `cp2kdata/md` 格式有兼容性问题（见 `app.log`）|
| `deepgen.sh` | 启动脚本 | 加载 `dp-gpu` 模块 → `nohup dpgen run` 后台运行 DP-GEN 工作流 |
| `input.inp` | CP2K 模板 | DP-GEN 中用于第一性原理计算的 CP2K 输入模板，支持 C/O/H/Li/P/F/N/S 元素，包含 `@include coord.xyz` 占位符 |
| `machine.json` | DP-GEN 集群配置 | 配置了 train/model_devi/fp 三阶段的 Slurm 资源（节点数、GPU/CPU、队列名、模块加载） |
| `param.json` | DP-GEN 参数 | 训练参数配置：元素类型、原子质量、初始数据路径、结构路径、模型数量（4个）、训练参数（DeepPot-SE 等） |
| `traindata/traindata` | **占位符**（空文件） | 训练数据目录标记 |
| `app.log` | 运行日志 | 记录 `cp2kdata/md` 格式解析失败的错误信息 |

---

### 📂 deepmd_kit/ — DeepMD-kit 训练与测试

| 文件 | 功能 | 说明 |
|------|------|------|
| `aimd/cp2k_dp.py` | Python 脚本 | AIMD 数据提取：从 CP2K 输出中读取轨迹/能量/力，转换为 DeepMD 训练格式 |
| `input.json` | 训练参数 | DeepMD 模型超参数配置（嵌入网络、拟合网络、学习率、损失函数等） |
| `dpkit.sh` / `dpkit.sh.bak` | 训练脚本 | `dp train input.json` 启动 DeepMD 训练 |
| `dptest.sh` | 测试脚本 | `dp test -m` 对训练好的模型进行精度测试 |
| `dpfreeze.sh` | 冻结脚本 | `dp freeze -o` 将训练好的模型冻结为 `frozen_model.pb` |
| `dpcompass.sh` | 模型评估 | `dp compress` 压缩模型以加速推理 |
| `dpkit_energy_fit.txt` | 能量拟合结果 | 训练过程中能量拟合误差记录 |
| `dpkit_force_fit.txt` | 力拟合结果 | 训练过程中力拟合误差记录 |
| `lammps/in.reax` | LAMMPS 输入 | 配合 DeepMD 势函数进行 ReaxFF 反应力场模拟的 LAMMPS 输入文件 |

---

### 📂 lammps/ — LAMMPS 输入文件

| 文件 | 功能 |
|------|------|
| `in.reax` | ReaxFF 反应力场 LAMMPS 输入文件 |

---

### 📂 reactnetwork/ — 反应网络分析 (ReacNetGenerator)

| 文件 | 功能 | 说明 |
|------|------|------|
| `reactnet.sh` | Linux 批量处理脚本 | 遍历子文件夹，对每个含 `.lammpstrj` 的目录运行 `reacnetgenerator --nohmm` |
| `auto_reactnet.sh` | 增强版处理脚本 | 完整流程：主目录反应网络 → 物种分析 → 轨迹切片 → 子目录反应网络 → 反应机理分析 |
| `reaction_mechanism.py` | Python 反应机理分析 | 解析 `.reaction` 文件，构建有向图，用 pyvis 生成交互式 HTML 网络图。支持频率阈值过滤、节点大小/线条粗细自定义 |
| `species_analyzer.py` | Python 物种分析 | 将 `.species` 文件转为 `.txt/.xlsx`，统计物种数和分子数 |
| `split.py` | Python 轨迹切片 | 将完整 `.lammpstrj` 按帧对切分为独立子文件夹 |
| `run_reacnet.slurm` | Slurm 任务脚本 | 集群批处理：通过 `SBATCH --array` 并行处理多个轨迹文件 |
| `submit_slurm_reactnet.sh` | Slurm 提交脚本 | 自动发现含 `.lammpstrj` 的子目录，生成任务清单并投递到 Slurm 队列 |
| `reactnet.sh.back.bak` | 备份 | 旧版脚本备份 |

#### windows/ — Windows GUI 版工具

| 文件 | 功能 |
|------|------|
| `反应机理网络生成.py` | Tkinter 图形界面：选择 `.reaction` 文件 → 生成交互式反应网络 HTML |
| `反应机理预处理-切片.py` | Tkinter 图形界面：轨迹文件分帧切片 |
| `物种数与分子数统计新.py` | Tkinter 图形界面：物种文件转换 + 化学式查询（RDKit/Open Babel） + 统计 |
| `物种数做图.py` | Tkinter 图形界面：物种数统计绘图，支持图例位置自定义，期刊级 Times New Roman 样式 |

---

### 📂 jupyter/ — Jupyter 环境配置

| 文件 | 功能 | 说明 |
|------|------|------|
| `requirements.txt` | Python 包依赖 | Jupyter 及相关科学计算库列表 |
| `reboot_jupyter.sh` | 重启脚本 | 重启 Jupyter 服务 |
| `update_env.sh` | 更新脚本 | 更新 conda 环境或安装新包 |

---

### 📂 syncthing/ — Syncthing 多用户同步

| 文件 | 功能 | 说明 |
|------|------|------|
| `setup_syncthing_users.sh` | 配置脚本 | 为所有非 root 用户自动配置 Syncthing，分配独立端口 (GUI 8385+，同步 22000+)，强制绑定到 `0.0.0.0` |
| `test_syncthing.sh` | 诊断脚本 | 检查所有用户 Syncthing 服务状态、进程、端口监听 |
| `syncthing_setup_20250701_163400.log` | 配置日志 | 2025-07-01 配置过程的完整日志 |
| `syncthing_access_20250701.log` | 访问信息 | 配置完成后各用户的 Web 界面地址和端口信息 |

---

### 📄 顶层 Shell 脚本

| 文件 | 功能 | 说明 |
|------|------|------|
| `cp2kcpu.sh` | CP2K CPU 批量提交 | Slurm 脚本：遍历所有 `.inp` 文件，每个创建独立目录，用 CPU 版 `cp2k.psmp` 计算 |
| `cp2kgpu.sh` | CP2K GPU 批量提交 | 同上，但加载 GPU 版 CP2K 模块 |
| `cp2k_speed_test.sh` | CP2K 性能测试 | 从 1 到最大物理核数逐步测试 CPU 性能，并对比 0/1 GPU 加速效果，结果排序输出 |
| `lmp-cpu+deemd.sh` | LAMMPS CPU 批量提交 | Slurm 脚本：加载 `lmp-cpu+deepmd` 模块，遍历 `in.*` 文件进行 DeepMD 加速的 LAMMPS 计算 |
| `lmp-gpu-kokkos+deepmd.sh` | LAMMPS GPU 批量提交 | 同上，加载 GPU+Kokkos 版 LAMMPS，检测 GPU 数量自动切换 |
| `lmp_speed_test.sh` | LAMMPS 性能测试 | 全面测试不同 CPU 核数与 GPU 数量的组合性能，自动检测 GPU 有无，结果记录到每个任务的独立 txt |
| `useradd.sh` | 创建用户 | 交互式脚本：创建新用户（家目录在 `/data/home/` 下），设置密码，更新 NIS 数据库 |

### 📄 顶层 Python 脚本

| 文件 | 功能 | 说明 |
|------|------|------|
| `energy.py` | 能量/活化能分析 | Tkinter 图形界面工具：Arrhenius 活化能拟合、数据可视化、期刊级出图、导出 Excel/图片。支持指数拟合、激活能计算 |

### 📄 配置文件

| 文件 | 功能 |
|------|------|
| `.gitignore` | 忽略仿真输出文件、大文件、系统文件等 |

---

## 文件归纳

### 按计算阶段

| 阶段 | 相关文件 |
|------|----------|
| 结构准备 | `cp2k/cp2k_AIMD.bat`, `cp2k/cp2k_Dpgen.bat`, `cp2k/cp2k_OS.bat`（需 Multiwfn + `.cif`） |
| 第一性原理计算 | `cp2k/Al_H2O_GAS.inp`, `deepgen/input.inp`, `cp2kcpu.sh`, `cp2kgpu.sh` |
| 势函数训练 | `deepgen/`（DP-GEN 工作流），`deepmd_kit/`（DeepMD 训练/测试/冻结/压缩） |
| 分子动力学 | `lammps/in.reax`, `lmp-cpu+deemd.sh`, `lmp-gpu-kokkos+deepmd.sh` |
| 性能测试 | `cp2k_speed_test.sh`, `lmp_speed_test.sh` |
| 轨迹分析 | `reactnetwork/`（ReacNetGenerator 反应网络分析） |
| 数据分析 | `energy.py`（活化能拟合与绘图） |
| 环境配置 | `jupyter/`, `syncthing/` |

### 按平台

| 平台 | 文件 |
|------|------|
| **Linux/Slurm 集群** | 所有 `.sh`/`.slurm` 脚本（smaster 服务器） |
| **Windows 桌面** | `reactnetwork/windows/` 下的 4 个 Tkinter GUI 脚本 |
| **跨平台** | `energy.py`（Tkinter GUI，可在任一平台运行） |

---

## 运行环境要求

- **集群**: Slurm 作业管理系统，已配置 `cp2k-cpu`、`cp2k-gpu`、`dp-gpu`、`lmp-cpu+deepmd`、`lmp-gpu-kokkos+deepmd` 等环境模块
- **Python**: Anaconda/conda 环境，依赖 `dpdata`、`rdkit`、`openbabel`、`pyvis`、`networkx`、`pandas`、`matplotlib`、`scipy`、`openpyxl`、`Pillow` 等
- **Windows 桌面**: Python 3，Tkinter，[Multiwfn](http://sobereva.com/multiwfn)（用于 `.cif` → CP2K 输入转换）
