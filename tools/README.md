# tools — 第三方/辅助工具

Materials Studio 辅助工具和 LAMMPS 力场转换工具。

## 目录结构

```
tools/
├── msi2lmp/                  # MSI2LMP（Materials Studio → LAMMPS 转换器）
│   ├── src/                  # C 源码（msi2lmp.c + 辅助模块）
│   ├── build/                # PyInstaller 构建产物（diaoyong1.exe）
│   ├── dist/                 # 编译后的 .exe 和转换结果 .data 文件
│   ├── frc_files/            # 力场文件库（cff91、pcff、cvff、oplsaa 等）
│   ├── README / readme1.txt  # 使用说明
│   └── diaoyong1.py / .spec  # 调用脚本
├── ms-perl/                  # Materials Studio Perl 脚本
│   ├── xlink-new-10ps.pl     # 交联脚本（10ps 交联）
│   ├── Dielectric constant.pl # 介电常数计算
│   ├── pureBPDA.std          # BPDA 单体模板
│   ├── User Menu.xml         # MS 菜单配置
│   └── crosslink.zip         # 交联脚本压缩包
├── BoltzmannInversion.pl     # Boltzmann 反演（粗粒化力场）
└── BoltzmannInversion2.1.pl  # Boltzmann 反演 v2.1
```

## 主要工具说明

### msi2lmp — MS 模型转 LAMMPS

Materials Studio 的 `.car/.mdf` 文件 → LAMMPS `.data` 文件格式转换。
- C 源码可自行编译，Windows 下提供了编译好的 `diaoyong1.exe`
- `frc_files/` 包含 8 个主流力场：cff91、pcff、cvff、oplsaa、compass、clayff 等
- `dist/` 存放转换后的 .data 文件和 SiC/石墨烯/合金等示例

### ms-perl — MS 自动化脚本

Materials Studio 的 Perl 脚本，需在 MS 中运行。
- `xlink-new-10ps.pl`：环氧树脂交联过程建模
- `Dielectric constant.pl`：介电常数计算

### BoltzmannInversion

粗粒化力场参数化工具：将全原子 RDF 反演为粗粒化势能。
