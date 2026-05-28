# ML — 机器学习相关脚本

深度学习势函数（DP-GEN）和传统机器学习脚本。

## 文件说明

| 文件 | 用途 |
|------|------|
| `CP2K2DP_GUI.py` | CP2K AIMD 输出 → DeepMD 训练数据格式。读取 CP2K 输出文件，随机分割为训练/验证集，输出为 DeepMD npy 格式 |
| `机器学习界面.py` | 机器学习回归模型 GUI。集成 Linear/Ridge/Lasso/RF/GBDT/SVR/KNN/MLP 等多种模型，支持交叉验证、学习曲线 |
| `predict图形化界面.py` | 加载已训练的 .joblib 模型进行预测的 GUI 工具 |
| `19-param注释.json` | DP-GEN 参数配置文件（含中文注释版本） |
| `param_abacus.json` | ABACUS 第一性原理计算的 DP-GEN 参数配置 |
