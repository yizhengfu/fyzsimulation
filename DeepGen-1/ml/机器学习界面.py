import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import os
import threading
import time
from datetime import datetime
import sys
from joblib import dump
import warnings

# 导入所有可用的回归模型
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, KFold, learning_curve
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

# 抑制警告信息
warnings.filterwarnings('ignore')


class AdaptiveKNN(KNeighborsRegressor):
    def fit(self, X, y):
        self.n_neighbors_ = min(self.n_neighbors, X.shape[0])
        return super().fit(X, y)


class ModelEvaluator:
    def __init__(self, X, y, cv_splits=5, target_name=""):
        self.X = X
        self.y = y
        self.feature_names = X.columns if isinstance(X, pd.DataFrame) else [f"Feature_{i}" for i in range(X.shape[1])]
        self.cv_splits = cv_splits
        self.target_name = target_name
        self.kf = KFold(n_splits=cv_splits, shuffle=True, random_state=42)
        self.models = self._get_models()
        self.results = []
        self.predictions = {}
        self.feature_importance = {}
        self.r2_scores = {}
        self.model_name_mapping = {
            'Linear Regression': '线性回归',
            'Ridge': '岭回归',
            'Lasso': 'Lasso回归',
            'ElasticNet': '弹性网络',
            'SGD Regressor': 'SGD回归器',
            'Random Forest': '随机森林',
            'Gradient Boosting': '梯度提升',
            'AdaBoost': 'AdaBoost',
            'SVR': '支持向量回归',
            'Decision Tree': '决策树',
            'KNN': 'K近邻',
            'Neural Network': '神经网络'
        }
        self.target_name_cn = target_name

    def _get_models(self):
        return {
            # 线性模型
            'Linear Regression': LinearRegression(),
            'Ridge': Ridge(alpha=0.1, random_state=42),
            'Lasso': Lasso(alpha=0.0000001, max_iter=10000000,
                           selection='cyclic', tol=1e-6, random_state=42),

            # 树模型
            'Random Forest': RandomForestRegressor(
                n_estimators=30, max_depth=3,
                min_samples_split=15, max_features=0.3,
                bootstrap=False, random_state=42
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=30, learning_rate=0.1,
                max_depth=2, min_samples_leaf=10,
                validation_fraction=0.25, n_iter_no_change=3,
                random_state=42
            ),

            # 其他模型
            'SVR': SVR(kernel='rbf', C=50, gamma=0.01,
                       epsilon=0.01, cache_size=1000),
            'KNN': AdaptiveKNN(n_neighbors=5),
            'Decision Tree': DecisionTreeRegressor(
                max_depth=3, min_samples_split=10,
                random_state=42
            )
        }

    def _get_feature_importance(self, name, model):
        """获取模型的特征重要性"""
        try:
            # 对于具有feature_importances_属性的模型（树类模型）
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                return pd.Series(importance, index=self.feature_names)

            # 对于线性模型，使用系数的绝对值
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
                return pd.Series(importance, index=self.feature_names)

            # 对于其他模型，使用permutation importance
            else:
                result = permutation_importance(model, self.X, self.y,
                                                n_repeats=10,
                                                random_state=42)
                importance = result.importances_mean
                return pd.Series(importance, index=self.feature_names)

        except Exception as e:
            print(f"无法计算{name}的特征重要性: {str(e)}")
            return None

    def plot_feature_importance(self, output_dir):
        """为每个模型绘制特征重要性图"""
        for name, importance in self.feature_importance.items():
            if importance is not None and not importance.empty:
                plt.figure(figsize=(10, 6))

                # 对特征重要性进行排序
                importance_sorted = importance.sort_values(ascending=True)

                # 创建水平条形图
                plt.barh(range(len(importance_sorted)), importance_sorted)

                # 添加特征名称标签
                plt.yticks(range(len(importance_sorted)), importance_sorted.index)

                # 在每个条形上添加数值标签
                for i, v in enumerate(importance_sorted):
                    plt.text(v, i, f'{v:.3f}',
                             va='center',
                             fontsize=8)

                plt.xlabel('Feature Importance')
                plt.title(f'Feature Importance - {name} ({self.target_name})')
                plt.tight_layout()

                # 保存图片
                chinese_name = self.model_name_mapping.get(name, name)
                plt.savefig(
                    os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_特征重要性.tiff'),
                    dpi=600,
                    format='tiff',
                    pil_kwargs={'compression': 'tiff_lzw'}
                )
                plt.close()

                # 保存特征重要性到CSV
                importance_df = pd.DataFrame({
                    'Feature': importance_sorted.index,
                    'Importance': importance_sorted.values
                })
                importance_df.to_csv(os.path.join(output_dir,
                                                  f'{self.target_name_cn}_{chinese_name}_特征重要性.csv'),
                                     index=False, encoding='utf-8')

                # 保存特征重要性数据到.dat文件
                with open(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_特征重要性.dat'), 'w',
                          encoding='utf-8') as f:
                    f.write("# Feature\tImportance\n")
                    for feature, imp in zip(importance_sorted.index, importance_sorted.values):
                        f.write(f"{feature}\t{imp:.6f}\n")

    def plot_learning_curves(self, output_dir):
        """为每个模型生成R²学习曲线"""
        # 定义训练集大小的比例
        train_sizes = np.linspace(0.1, 1.0, 10)

        for name, model in self.models.items():
            print(f"Generating learning curve for {name}...")
            try:
                # 计算学习曲线
                train_sizes_abs, train_scores, test_scores = learning_curve(
                    model, self.X, self.y,
                    train_sizes=train_sizes,
                    cv=self.cv_splits,
                    scoring='r2',
                    n_jobs=-1
                )

                # 计算平均值和标准差
                train_mean = np.mean(train_scores, axis=1)
                train_std = np.std(train_scores, axis=1)
                test_mean = np.mean(test_scores, axis=1)
                test_std = np.std(test_scores, axis=1)

                # 绘制学习曲线
                plt.figure(figsize=(10, 6))
                plt.plot(train_sizes_abs, train_mean, label='Training Score', color='blue', marker='o')
                plt.fill_between(train_sizes_abs, train_mean - train_std, train_mean + train_std, alpha=0.1,
                                 color='blue')
                plt.plot(train_sizes_abs, test_mean, label='Cross-validation Score', color='red', marker='o')
                plt.fill_between(train_sizes_abs, test_mean - test_std, test_mean + test_std, alpha=0.1, color='red')

                plt.xlabel('Training Examples')
                plt.ylabel('R² Score')
                plt.title(f'Learning Curve - {name} ({self.target_name})')
                plt.legend(loc='lower right')
                plt.grid(True)
                plt.tight_layout()

                # 保存图形
                chinese_name = self.model_name_mapping.get(name, name)
                plt.savefig(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_学习曲线.tiff'),
                            dpi=600,
                            format='tiff',
                            pil_kwargs={'compression': 'tiff_lzw'}
                            )
                plt.close()

                # 保存学习曲线数据到.dat文件
                with open(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_学习曲线.dat'), 'w',
                          encoding='utf-8') as f:
                    f.write("# TrainSize\tTrainScore\tTrainStd\tTestScore\tTestStd\n")
                    for i in range(len(train_sizes_abs)):
                        f.write(
                            f"{train_sizes_abs[i]}\t{train_mean[i]:.6f}\t{train_std[i]:.6f}\t{test_mean[i]:.6f}\t{test_std[i]:.6f}\n")

            except Exception as e:
                print(f"Error generating learning curve for {name}: {str(e)}")

    def evaluate_model(self, name, model, log_callback=None):
        if log_callback:
            log_callback(f"正在评估 {name} 模型...")
        start_time = time.time()

        # 确保交叉验证正确执行
        try:
            r2_scores = cross_val_score(model, self.X, self.y, cv=self.kf, scoring='r2')
            rmse_scores = np.sqrt(-cross_val_score(model, self.X, self.y, cv=self.kf, scoring='neg_mean_squared_error'))
        except Exception as e:
            if log_callback:
                log_callback(f"交叉验证失败: {str(e)}")
            return None  # 返回空值避免后续错误

        # 全量训练集预测
        model.fit(self.X, self.y)
        y_pred = model.predict(self.X)
        self.predictions[name] = y_pred

        # 计算训练集R²
        r2_train = r2_score(self.y, y_pred)
        self.r2_scores[name] = r2_train  # 存储到字典

        # 计算特征重要性
        self.feature_importance[name] = self._get_feature_importance(name, model)

        training_time = time.time() - start_time

        return {
            'Model': name,
            'Mean R²': r2_scores.mean(),
            'Std R²': r2_scores.std() * 2,
            'Mean RMSE': rmse_scores.mean(),
            'Std RMSE': rmse_scores.std() * 2,
            'Training R²': r2_train,
            'Training Time (s)': training_time
        }

    def plot_results(self, output_dir, log_callback=None):
        """生成所有可视化图表并保存数据点"""
        if log_callback:
            log_callback("正在生成结果可视化...")

        # 1. 模型性能对比条形图
        plt.figure(figsize=(12, 6))
        results_df = pd.DataFrame(self.results)
        plt.barh(results_df['Model'], results_df['Mean R²'])
        plt.title(f'Model Performance Comparison - {self.target_name}')
        plt.xlabel('R² Score')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{self.target_name_cn}_模型对比.tiff'),
                    dpi=600,
                    format='tiff',
                    pil_kwargs={'compression': 'tiff_lzw'}
                    )
        plt.close()

        # 保存模型性能对比数据
        results_df.to_csv(os.path.join(output_dir, f'{self.target_name_cn}_模型对比.dat'),
                          sep='\t', index=False, encoding='utf-8',
                          columns=['Model', 'Mean R²', 'Mean RMSE'])

        # 2. 实际值vs预测值散点图
        for name, y_pred in self.predictions.items():
            plt.figure(figsize=(8, 6))
            plt.scatter(self.y, y_pred, alpha=0.5)
            plt.plot([self.y.min(), self.y.max()], [self.y.min(), self.y.max()], 'r--')
            # 添加R²标注
            r2_value = self.r2_scores.get(name, np.nan)
            plt.text(
                x=0.95,
                y=0.05,
                s=f'$R^2 = {r2_value:.3f}$',
                transform=plt.gca().transAxes,
                fontsize=12,
                fontweight='bold',
                ha='right',
                va='bottom',
                bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8)
            )
            plt.xlabel('Actual Values')
            plt.ylabel('Predicted Values')
            plt.title(f'{name} - Actual vs Predicted ({self.target_name})')
            plt.tight_layout()
            chinese_name = self.model_name_mapping.get(name, name)
            plt.savefig(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_散点图.tiff'),
                        dpi=600,
                        format='tiff',
                        pil_kwargs={'compression': 'tiff_lzw'}
                        )
            plt.close()

            # 保存实际值vs预测值的数据点到.dat文件
            with open(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_散点图.dat'), 'w',
                      encoding='utf-8') as f:
                f.write("# ActualValue\tPredictedValue\n")
                for actual, pred in zip(self.y, y_pred):
                    f.write(f"{actual:.6f}\t{pred:.6f}\n")

        # 3. 预测误差分布图
        for name, y_pred in self.predictions.items():
            plt.figure(figsize=(8, 6))
            errors = self.y - y_pred
            sns.histplot(errors, kde=True)
            plt.title(f'{name} - Prediction Error Distribution ({self.target_name})')
            plt.xlabel('Prediction Error')
            plt.tight_layout()
            chinese_name = self.model_name_mapping.get(name, name)
            plt.savefig(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_误差分布.tiff'),
                        dpi=600,
                        format='tiff',
                        pil_kwargs={'compression': 'tiff_lzw'}
                        )
            plt.close()

            # 保存误差分布数据到.dat文件
            with open(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_误差分布.dat'), 'w',
                      encoding='utf-8') as f:
                f.write("# Error\n")
                for error in errors:
                    f.write(f"{error:.6f}\n")

            # 另外保存一个带索引的误差数据文件，方便与原始数据对应
            error_df = pd.DataFrame({
                'ActualValue': self.y,
                'PredictedValue': y_pred,
                'Error': errors
            })
            error_df.to_csv(os.path.join(output_dir, f'{self.target_name_cn}_{chinese_name}_详细误差.dat'),
                            sep='\t', index=False, encoding='utf-8')

        # 4. 添加学习曲线
        if log_callback:
            log_callback("正在生成学习曲线...")
        self.plot_learning_curves(output_dir)

        # 5. 添加特征重要性图
        if log_callback:
            log_callback("正在生成特征重要性图...")
        self.plot_feature_importance(output_dir)

    def evaluate_all_models(self, log_callback=None):
        """评估所有模型并返回结果DataFrame"""
        for name, model in self.models.items():
            try:
                result = self.evaluate_model(name, model, log_callback)
                if result is not None:  # 跳过失败模型
                    self.results.append(result)
            except Exception as e:
                if log_callback:
                    log_callback(f"评估 {name} 出错: {str(e)}")

        # 检查结果是否为空
        if not self.results:
            error_msg = "所有模型评估失败，请检查数据或参数配置！"
            if log_callback:
                log_callback(error_msg)
            raise ValueError(error_msg)

        results_df = pd.DataFrame(self.results)
        results_df = results_df.sort_values('Mean R²', ascending=False)
        return results_df


def create_results_directory(data_filename):
    """创建结果目录，使用中文命名"""
    # 获取文件名（不包含扩展名）
    base_name = os.path.splitext(os.path.basename(data_filename))[0]

    # 创建目录名：文件名_评估结果_日期时间
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"{base_name}_评估结果_{timestamp}"

    # 创建目录
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


class ModelEvaluationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("机器学习模型评估工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 设置字体
        self.default_font = ('Microsoft YaHei UI', 10)
        self.header_font = ('Microsoft YaHei UI', 12, 'bold')

        # 数据存储
        self.data = None
        self.file_path = None

        # 创建UI
        self.create_widgets()

        # 窗口居中
        self.center_window()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部栏 - 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="数据文件", padding="5")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        # 文件选择按钮和路径显示
        ttk.Button(file_frame, text="选择CSV文件", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(file_frame, text="未选择文件", width=70)
        self.file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 中间区域 - 列选择
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧 - 特征选择
        feature_frame = ttk.LabelFrame(selection_frame, text="选择特征变量", padding="5")
        feature_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 特征列表框和滚动条
        feature_scroll = ttk.Scrollbar(feature_frame)
        feature_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.feature_listbox = tk.Listbox(feature_frame, selectmode=tk.MULTIPLE,
                                          yscrollcommand=feature_scroll.set, exportselection=0)
        self.feature_listbox.pack(fill=tk.BOTH, expand=True)
        feature_scroll.config(command=self.feature_listbox.yview)

        # 选择控制按钮
        feature_btn_frame = ttk.Frame(feature_frame)
        feature_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(feature_btn_frame, text="全选", command=lambda: self.select_all(self.feature_listbox)).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(feature_btn_frame, text="取消全选", command=lambda: self.deselect_all(self.feature_listbox)).pack(
            side=tk.LEFT)

        # 右侧 - 目标变量选择
        target_frame = ttk.LabelFrame(selection_frame, text="选择目标变量", padding="5")
        target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        target_scroll = ttk.Scrollbar(target_frame)
        target_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.target_listbox = tk.Listbox(target_frame, selectmode=tk.MULTIPLE,
                                         yscrollcommand=target_scroll.set, exportselection=0)
        self.target_listbox.pack(fill=tk.BOTH, expand=True)
        target_scroll.config(command=self.target_listbox.yview)

        # 参数设置框架
        param_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="5")
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        # CV折数
        cv_frame = ttk.Frame(param_frame)
        cv_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cv_frame, text="交叉验证折数:").pack(side=tk.LEFT, padx=5)
        self.cv_var = tk.StringVar(value="5")
        cv_spinbox = ttk.Spinbox(cv_frame, from_=2, to=20, textvariable=self.cv_var, width=5)
        cv_spinbox.pack(side=tk.LEFT)

        # 标准化选项
        self.normalize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(param_frame, text="对特征进行标准化", variable=self.normalize_var).pack(anchor=tk.W, padx=5)

        # 底部区域 - 日志和按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 日志区域
        log_frame = ttk.LabelFrame(bottom_frame, text="执行日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        self.run_button = ttk.Button(button_frame, text="开始评估", command=self.run_evaluation)
        self.run_button.pack(side=tk.RIGHT, padx=5)
        self.run_button["state"] = "disabled"

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log(self, message):
        """在日志文本框中添加消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()

    def load_csv(self):
        """加载CSV文件并更新列选择"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )

        if not file_path:
            return

        try:
            # 加载数据
            self.data = pd.read_csv(file_path)
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))

            # 更新列选择列表
            self.update_column_listboxes()

            # 启用运行按钮
            self.run_button["state"] = "normal"

            # 更新状态
            self.status_var.set(
                f"已加载数据集: {os.path.basename(file_path)} ({len(self.data)} 行 x {len(self.data.columns)} 列)")
            self.log(f"已加载数据集: {file_path}")
            self.log(f"数据维度: {self.data.shape}")

        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错: {str(e)}")
            self.log(f"错误: {str(e)}")

    def update_column_listboxes(self):
        """更新特征和目标列表选择框"""
        if self.data is None:
            return

        # 清空列表
        self.feature_listbox.delete(0, tk.END)
        self.target_listbox.delete(0, tk.END)

        # 添加所有列
        for col in self.data.columns:
            self.feature_listbox.insert(tk.END, col)
            self.target_listbox.insert(tk.END, col)

    def select_all(self, listbox):
        """全选列表中的所有项"""
        listbox.selection_set(0, tk.END)

    def deselect_all(self, listbox):
        """取消所有选择"""
        listbox.selection_clear(0, tk.END)

    def run_evaluation(self):
        """运行模型评估"""
        # 获取所选特征和目标
        selected_features = [self.feature_listbox.get(i) for i in self.feature_listbox.curselection()]
        selected_targets = [self.target_listbox.get(i) for i in self.target_listbox.curselection()]

        # 验证选择
        if not selected_features:
            messagebox.showwarning("警告", "请至少选择一个特征变量！")
            return

        if not selected_targets:
            messagebox.showwarning("警告", "请至少选择一个目标变量！")
            return

        # 检查交叉验证折数
        try:
            cv_splits = int(self.cv_var.get())
            if cv_splits < 2:
                raise ValueError("交叉验证折数必须大于或等于2")
        except Exception as e:
            messagebox.showerror("参数错误", f"无效的交叉验证折数: {str(e)}")
            return

        # 禁用UI
        self.run_button["state"] = "disabled"
        self.status_var.set("评估中...")

        # 创建结果目录
        output_dir = create_results_directory(self.file_path)
        self.log(f"创建结果目录: {output_dir}")

        # 启动评估线程
        threading.Thread(target=self._execute_evaluation,
                         args=(selected_features, selected_targets, cv_splits, output_dir)).start()

    def _execute_evaluation(self, features, targets, cv_splits, output_dir):
        """在单独的线程中执行模型评估"""
        try:
            # 准备数据
            X = self.data[features]

            # 设置字体等
            plt.rcParams.update({
                'font.family': 'serif',
                'font.serif': ['Times New Roman'],
                'font.sans-serif': ['SimHei', 'DejaVu Sans'],
                'axes.titleweight': 'bold',
                'axes.labelweight': 'bold',
                'axes.unicode_minus': False
            })

            # 标准化处理
            if self.normalize_var.get():
                self.log("正在进行特征标准化...")
                scaler = StandardScaler()
                X_scaled = pd.DataFrame(
                    scaler.fit_transform(X),
                    columns=X.columns
                )
                # 保存标准化器
                dump(scaler, os.path.join(output_dir, 'scaler.joblib'))
                self.log("标准化器已保存")
            else:
                X_scaled = X

            # 保存特征列表
            feature_df = pd.DataFrame({'Feature': X.columns})
            feature_df.to_csv(os.path.join(output_dir, '特征列表.csv'), index=False, encoding='utf-8')
            feature_df.to_csv(os.path.join(output_dir, '特征列表.dat'), sep='\t', index=False, encoding='utf-8')

            # 对每个目标变量执行评估
            all_results = {}
            best_models = {}

            for target_name in targets:
                self.log(f"\n开始评估目标变量: {target_name}")
                y = self.data[target_name]

                # 创建评估器
                evaluator = ModelEvaluator(X_scaled, y, cv_splits=cv_splits, target_name=target_name)

                # 评估所有模型
                results_df = evaluator.evaluate_all_models(log_callback=self.log)
                all_results[target_name] = results_df

                # 保存结果
                results_df.to_csv(os.path.join(output_dir, f'{target_name}_评估结果.csv'),
                                  index=False, encoding='utf-8')
                results_df.to_csv(os.path.join(output_dir, f'{target_name}_评估结果.dat'),
                                  sep='\t', index=False, encoding='utf-8')

                # 生成可视化
                evaluator.plot_results(output_dir, log_callback=self.log)

                # 获取最佳模型
                best_model_name = results_df.iloc[0]['Model']
                best_models[target_name] = {
                    'name': best_model_name,
                    'model': evaluator.models[best_model_name],
                    'R2': results_df.iloc[0]['Mean R²'],
                    'RMSE': results_df.iloc[0]['Mean RMSE']
                }

                # 保存最佳模型
                dump(evaluator.models[best_model_name],
                     os.path.join(output_dir, f'best_model_{target_name}.joblib'))

                self.log(f"完成 {target_name} 的评估")
                self.log(f"最佳模型: {best_model_name}, R²: {results_df.iloc[0]['Mean R²']:.4f}")

            # 保存最佳模型总结
            with open(os.path.join(output_dir, '最佳模型总结.txt'), 'w', encoding='utf-8') as f:
                for target, model_info in best_models.items():
                    f.write(f"Target: {target}\n")
                    f.write(f"Best Model: {model_info['name']}\n")
                    f.write(f"R² Score: {model_info['R2']:.6f}\n")
                    f.write(f"RMSE: {model_info['RMSE']:.6f}\n\n")

            # 完成
            self.log(f"\n评估完成! 结果已保存到: {output_dir}")
            messagebox.showinfo("完成", f"模型评估已完成!\n结果保存在:\n{output_dir}")

            # 尝试打开结果文件夹
            try:
                if sys.platform == 'win32':
                    os.startfile(output_dir)
                elif sys.platform == 'darwin':  # macOS
                    os.system(f'open "{output_dir}"')
                else:  # Linux
                    os.system(f'xdg-open "{output_dir}"')
            except:
                pass

        except Exception as e:
            error_msg = f"执行评估时出错: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("错误", error_msg)
        finally:
            # 重新启用UI
            self.root.after(0, lambda: self.run_button.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("就绪"))


def main():
    root = tk.Tk()
    app = ModelEvaluationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()