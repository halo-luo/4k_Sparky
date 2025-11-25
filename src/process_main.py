import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import multiprocessing as mp
import queue
import numpy as np
from ultralytics import YOLO
import os


# --------------------- 子进程函数（专门跑 YOLO） ---------------------
def yolo_worker(input_queue: mp.Queue, output_queue: mp.Queue, model_path: str):
    """子进程：加载模型 + 持续监听任务"""
    print(f"[子进程] 正在加载模型: {model_path}")
    model = YOLO(model_path)
    print("[子进程] 模型加载完成，等待任务...")

    while True:
        try:
            task = input_queue.get()  # 接收任务
            if task is None:  # 退出信号
                print("[子进程] 收到退出信号，关闭")
                break

            frame = task  # 直接是 numpy 数组（BGR）
            results = model(frame, verbose=False, conf=0.4)[0]
            annotated_frame = results.plot(line_width=2)

            # 把画好的图发回主进程
            output_queue.put(annotated_frame)

        except Exception as e:
            output_queue.put(None)
            print(f"[子进程错误] {e}")


class ShowSparky:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sparky - 多进程 YOLO 实时检测")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.img_path_dict = {}
        self.photo = None

        # 多进程通信队列
        self.task_queue = mp.Queue()
        self.result_queue = mp.Queue()

        # 启动子进程
        self.worker_process = mp.Process(
            target=yolo_worker,
            args=(self.task_queue, self.result_queue, "./yolov8s.pt"),
            daemon=True
        )
        self.worker_process.start()
        print("[主进程] YOLO 子进程已启动")

        # 定时检查结果队列
        self.root.after(100, self.check_result_queue)

    def check_result_queue(self):
        """每 10ms 检查一次结果队列"""
        try:
            while True:  # 一次性取完所有结果
                result_frame = self.result_queue.get_nowait()
                if result_frame is not None and isinstance(result_frame, np.ndarray):
                    self.display_frame(result_frame)
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self.check_result_queue)  # 持续轮询

    def display_frame(self, frame_bgr):
        """把子进程传回的带框图显示到 Label"""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pil_img.thumbnail((750, 550), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(pil_img)
        self.img_label.config(image=self.photo, text="")

    def update_img_label(self, img):
        img.thumbnail((750, 550))
        self.photo = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.photo, text="")

    def show_4k(self):
        """从摄像头抓一帧，扔给子进程处理"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("错误", "无法打开摄像头！")
            return

        ret, frame = cap.read()
        cap.release()
        if not ret:
            messagebox.showwarning("警告", "无法读取摄像头画面")
            return

        # 把帧发给子进程处理（不等待！）
        try:
            self.task_queue.put(frame, block=False)
        except queue.Full:
            pass  # 队列满就丢帧，防止堆积

    def img_combo_on_select(self, event=None):
        selected = self.img_combo.get()
        if selected == "4K":
            self.show_4k()  # 扔给子进程，不卡！
            return

        img_path = self.img_path_dict[selected]
        if os.path.exists(img_path):
            img = Image.open(img_path)
            self.update_img_label(img)
        else:
            self.img_label.config(text="图片不存在", image="")

    def create_widgets(self):
        self.img_path_dict = {
            "360P": "../img/360.jpg",
            "480P": "../img/480.jpg",
            "1080P": "../img/1080.jpg",
            "4K": ""
        }

        self.img_combo = ttk.Combobox(
            self.root, values=list(self.img_path_dict.keys()), state="readonly", font=("微软雅黑", 12)
        )
        self.img_combo.pack(pady=15)
        self.img_combo.current(0)
        self.img_combo.bind("<<ComboboxSelected>>", self.img_combo_on_select)

        self.img_label = tk.Label(
            self.root, text="选择分辨率查看效果", bg="white", width=80, height=30,
            relief="sunken", anchor="center", font=("微软雅黑", 14)
        )
        self.img_label.pack(pady=10, padx=30, fill="both", expand=True)

        # 提示标签
        tip = tk.Label(self.root, text="选择 4K → 实时打开摄像头进行 YOLO 检测（不卡界面！）", fg="blue")
        tip.pack(pady=5)

    def run(self):
        self.create_widgets()
        self.img_combo_on_select(None)

    def close(self):
        """程序关闭时优雅终止子进程"""
        self.task_queue.put(None)  # 发送退出信号
        if self.worker_process.is_alive():
            self.worker_process.terminate()
            self.worker_process.join(timeout=2)
        self.root.quit()


if __name__ == '__main__':
    print("Sparky 启动中...")
    mp.set_start_method('spawn', force=True)  # Windows 必须这句！

    window = tk.Tk()
    app = ShowSparky(window)
    window.protocol("WM_DELETE_WINDOW", app.close)  # 点×时优雅退出
    app.run()
    window.mainloop()
