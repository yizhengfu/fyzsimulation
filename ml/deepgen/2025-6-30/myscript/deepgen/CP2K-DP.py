import os
import logging
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Optional
import dpdata
import numpy as np

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    TkinterDnD = None

# 配置日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProcessingThread(threading.Thread):
    def __init__(self, task_queue, progress_queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.progress_queue = progress_queue
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=0.1)
                self.process_task(task)
            except queue.Empty:
                continue

    def process_task(self, task):
        try:
            input_path, output_path, cp2k_file, ratio = task

            def update_progress(step, message):
                self.progress_queue.put(('progress', step, message))

            # 读取数据
            update_progress(10, "正在读取CP2K输出文件...")
            system = dpdata.LabeledSystem(
                str(input_path),
                fmt='cp2kdata/md',
                cp2k_output_name=cp2k_file.name
            )

            # 发送总帧数信息
            total_frames = len(system)
            self.progress_queue.put(('frame_info', total_frames))

            # 计算验证帧数
            validation_frames = max(1, min(
                int(round(total_frames * ratio)),
                total_frames - 1
            ))

            # 分割数据集
            update_progress(40, "随机分配数据集中...")
            val_indices = np.random.choice(total_frames, validation_frames, False)
            train_indices = np.setdiff1d(np.arange(total_frames), val_indices)

            train_system = system.sub_system(train_indices)
            val_system = system.sub_system(val_indices)

            # 保存数据
            update_progress(70, "保存数据集中...")
            output_path.mkdir(parents=True, exist_ok=True)

            train_path = output_path / "training_data"
            val_path = output_path / "validation_data"

            train_system.to_deepmd_npy(str(train_path))
            val_system.to_deepmd_npy(str(val_path))

            update_progress(100, "处理完成！")

        except Exception as e:
            logger.exception("处理过程中发生错误")
            self.progress_queue.put(('error', str(e)))

    def stop(self):
        self._stop_event.set()


class CP2KDataProcessor:
    def __init__(self, root):
        self.root = root if TkinterDnD is None else TkinterDnD.Tk()
        self.root.title("CP2K数据处理工具 v5.0")
        self.selected_out_file = tk.StringVar()
        self.total_frames_var = tk.StringVar(value="等待数据读取...")
        self.processing_thread: Optional[ProcessingThread] = None
        self.task_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.setup_ui()
        self.setup_dnd()
        self.start_progress_polling()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输入路径部分
        input_frame = ttk.LabelFrame(main_frame, text="路径设置")
        input_frame.pack(fill=tk.X, pady=5)

        # 输入文件夹
        ttk.Label(input_frame, text="输入文件夹:").grid(row=0, column=0, sticky="e")
        self.folder_path_entry = ttk.Entry(input_frame, width=50)
        self.folder_path_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="浏览", command=self.browse_input_folder).grid(row=0, column=2)

        # 输出文件夹
        ttk.Label(input_frame, text="输出文件夹:").grid(row=1, column=0, sticky="e")
        self.output_folder_entry = ttk.Entry(input_frame, width=50)
        self.output_folder_entry.grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="浏览", command=self.browse_output_folder).grid(row=1, column=2)

        # 处理参数部分
        param_frame = ttk.LabelFrame(main_frame, text="处理参数")
        param_frame.pack(fill=tk.X, pady=5)

        # 验证比例
        ttk.Label(param_frame, text="验证比例 (0.1-0.2):").grid(row=0, column=0, sticky="e")
        self.validation_ratio_entry = ttk.Entry(param_frame, width=8)
        self.validation_ratio_entry.insert(0, "0.2")
        self.validation_ratio_entry.grid(row=0, column=1, sticky="w")
        self.validation_ratio_entry.bind("<KeyRelease>", self.validate_ratio_input)

        # 文件选择部分
        file_sel_frame = ttk.Frame(param_frame)
        file_sel_frame.grid(row=1, columnspan=3, pady=5, sticky="ew")

        self.select_out_btn = ttk.Button(
            file_sel_frame,
            text="手动选择.out文件",
            command=self.select_out_file,
            state=tk.DISABLED
        )
        self.select_out_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(file_sel_frame, textvariable=self.selected_out_file,
                  foreground="blue", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)

        # 数据信息
        info_frame = ttk.Frame(param_frame)
        info_frame.grid(row=2, columnspan=3, pady=5, sticky="w")
        ttk.Label(info_frame, textvariable=self.total_frames_var).pack()

        # 控制按钮
        self.process_btn = ttk.Button(param_frame, text="开始处理", command=self.start_processing)
        self.process_btn.grid(row=3, columnspan=3, pady=10)

        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        self.status_label = ttk.Label(progress_frame, text="准备就绪")
        self.status_label.pack()

        # 日志输出
        result_frame = ttk.LabelFrame(main_frame, text="处理日志")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.result_text = tk.Text(result_frame, height=12, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_input_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, path)
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, path)
            self.auto_detect_outfile()

    def browse_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, path)

    def setup_dnd(self):
        if TkinterDnD is not None:
            self.folder_path_entry.drop_target_register(DND_FILES)
            self.folder_path_entry.dnd_bind('<<Drop>>', self.handle_dnd)

    def handle_dnd(self, event):
        paths = [p.strip('{}') for p in event.data.split()]
        valid_paths = [p for p in paths if os.path.isdir(p)]
        if valid_paths:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, valid_paths[0])
            self.auto_detect_outfile()

    def start_progress_polling(self):
        def check_progress():
            try:
                while True:
                    progress = self.progress_queue.get_nowait()
                    self.handle_progress_update(progress)
            except queue.Empty:
                pass
            finally:
                self.root.after(100, check_progress)

        self.root.after(100, check_progress)

    def handle_progress_update(self, progress):
        msg_type = progress[0]

        if msg_type == 'progress':
            _, value, message = progress
            self.progress_bar['value'] = value
            self.status_label.config(text=message)
        elif msg_type == 'frame_info':
            total_frames = progress[1]
            self.total_frames_var.set(f"总帧数: {total_frames:,}")
        elif msg_type == 'error':
            self.update_status(f"错误: {progress[1]}", is_error=True)
            self.progress_bar.stop()
            self.process_btn.config(state=tk.NORMAL)
        else:
            logger.warning(f"未知的进度消息类型: {msg_type}")

    def validate_ratio_input(self, event=None):
        try:
            ratio = float(self.validation_ratio_entry.get())
            valid = 0.1 <= ratio <= 0.2
            self.validation_ratio_entry.config(foreground="green" if valid else "red")
            return valid
        except:
            self.validation_ratio_entry.config(foreground="red")
            return False

    def select_out_file(self):
        initial_dir = self.folder_path_entry.get() or os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="选择CP2K输出文件",
            filetypes=(("OUT files", "*.out"), ("All files", "*.*"))
        )
        if file_path:
            self.selected_out_file.set(Path(file_path).name)
            self.select_out_btn.config(state=tk.DISABLED)

    def auto_detect_outfile(self):
        try:
            input_path = Path(self.folder_path_entry.get())
            if not input_path.exists():
                return

            out_files = list(input_path.glob("*.out"))
            if len(out_files) == 1:
                self.selected_out_file.set(out_files[0].name)
                self.select_out_btn.config(state=tk.DISABLED)
            elif len(out_files) > 1:
                self.select_out_btn.config(state=tk.NORMAL)
                self.selected_out_file.set("检测到多个.out文件，请手动选择！")
        except:
            pass

    def start_processing(self):
        self.prepare_processing()
        self.process_btn.config(state=tk.DISABLED)
        self.processing_thread = ProcessingThread(self.task_queue, self.progress_queue)
        self.processing_thread.start()

    def prepare_processing(self):
        try:
            input_path = Path(self.folder_path_entry.get())
            output_path = Path(self.output_folder_entry.get())
            ratio = float(self.validation_ratio_entry.get())

            # 参数验证
            if not input_path.exists():
                raise FileNotFoundError(f"输入路径不存在: {input_path}")
            if not self.validate_ratio_input():
                raise ValueError("验证比例必须在0.1到0.2之间")
            if not self.selected_out_file.get():
                raise ValueError("请选择输出文件")

            cp2k_file = input_path / self.selected_out_file.get()
            if not cp2k_file.exists():
                raise FileNotFoundError(f"输出文件不存在: {cp2k_file}")

            self.task_queue.put((input_path, output_path, cp2k_file, ratio))
            self.update_status("开始处理...")

        except Exception as e:
            self.update_status(f"参数错误: {str(e)}", is_error=True)
            logger.error(f"参数错误: {str(e)}")

    def update_status(self, message, is_error=False):
        self.status_label.config(
            text=message,
            foreground="red" if is_error else "black"
        )
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    app = CP2KDataProcessor(root)
    root.mainloop()