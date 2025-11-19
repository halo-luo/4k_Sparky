# import tkinter as tk
# from tkinter import filedialog, messagebox, scrolledtext
# from tkinter import ttk
# from PIL import Image, ImageTk
# import cv2
#
#
# def open_img(img_path):
#     img = None
#     try:
#         img = Image.open(img_path)
#     except Exception as e:
#         messagebox.showerror(f"图片路径错误:{e}")
#     return img
#
#
# class ShowSparky:
#     def __init__(self, root: tk.Tk):
#         self.root = root
#         self.root.title("Sparky")
#         self.root.geometry("800x600")
#         self.root.configure(bg="#f0f0f0")
#         self.root.resizable(False, False)
#
#         self.img_path_dict = {}
#
#         # 图片清晰度选择按钮
#         self.img_combo = None
#         # 图片显示区域
#         self.img_label = None
#         self.photo = None
#
#     def update_img_label(self, img):
#         img.thumbnail((550, 400))  # 限制最大尺寸
#         self.photo = ImageTk.PhotoImage(img)
#         self.img_label.config(image=self.photo, text="")
#
#     def show_4k(self):
#         try:
#             # 调用摄像头
#             cap = cv2.VideoCapture(0)
#             # 检查摄像头是否成功打开
#             if not cap.isOpened():
#                 print("错误：无法打开摄像头！检查是否被占用或驱动是否正常")
#
#             ret, frame = cap.read()  # 读取一帧
#             if not ret:
#                 print("无法读取画面（摄像头断开？）")
#             # 释放资源
#             cap.release()
#             print("摄像头已关闭")
#
#             img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#             self.update_img_label(img)
#
#         except Exception as e:
#             messagebox.showerror(f"<UNK>:{e}")
#
#     def img_combo_on_select(self, event=None):
#         selected = self.img_combo.get()
#         if selected == "4K":
#             self.show_4k()
#             return
#         img_path = self.img_path_dict[selected]
#         img = open_img(img_path)
#         self.update_img_label(img)
#
#     def create_widgets(self):
#         self.img_path_dict = {
#             "360P": "../img/360.jpg",
#             "480P": "../img/480.jpg",
#             "1080P": "../img/1080.jpg",
#             "4K": ""
#         }
#
#         img_combo_options = list(self.img_path_dict.keys())
#         self.img_combo = ttk.Combobox(
#             self.root, values=img_combo_options, state="readonly",
#         )
#         self.img_combo.pack()
#         self.img_combo.current(0)
#         self.img_combo.bind("<<ComboboxSelected>>", self.img_combo_on_select)  # 绑定选中事件
#
#         # === 图片显示区域 ===
#         self.img_label = tk.Label(
#             self.root, text="未选择图片", bg="white", width=600, height=600,
#             relief="sunken", anchor="center")
#         self.img_label.pack(pady=10, padx=20, fill="both", expand=False)
#
#     def run(self):
#         self.create_widgets()
#         self.img_combo_on_select(None)
#
#
# if __name__ == '__main__':
#     print("hello Sparky")
#     window = tk.Tk()
#     sparky = ShowSparky(window)
#     sparky.run()
#     window.mainloop()


import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading  # 用线程避免阻塞


class ShowSparky:
    def __init__(self, root):
        self.root = root
        self.root.title("Sparky - 支持实时摄像头")
        self.root.geometry("900x700")

        self.cap = None  # 摄像头对象
        self.camera_running = False
        self.img_label = None
        self.photo = None
        self.img_combo = None

        self.img_path_dict = {
            "360P": "../img/360.jpg",
            "480P": "../img/480.jpg",
            "1080P": "../img/1080.jpg",
            "4K": "camera"  # 特殊标记，表示用摄像头
        }

    def update_camera_frame(self):
        if self.camera_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (800, 600))
                img = Image.fromarray(frame)
                self.photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.photo, text="")
            # 每 10ms 更新一次（约 100fps，上限受摄像头限制）
            self.root.after(500, self.update_camera_frame)

    def start_camera(self):
        if self.camera_running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开摄像头！")
            return
        self.camera_running = True
        self.update_camera_frame()  # 开始循环更新

    def stop_camera(self):
        self.camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.img_label.config(image="", text="摄像头已关闭")

    def img_combo_on_select(self, event=None):
        selected = self.img_combo.get()

        # 先停止摄像头（避免多个来源冲突）
        self.stop_camera()

        if selected == "4K":
            self.start_camera()
        else:
            img_path = self.img_path_dict[selected]
            try:
                img = Image.open(img_path)
                img.thumbnail((800, 600))
                self.photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.photo, text="")
            except Exception as e:
                messagebox.showerror("错误", f"图片加载失败：{e}")

    def create_widgets(self):
        ttk.Label(self.root, text="选择清晰度：", font=("微软雅黑", 14)).pack(pady=10)

        self.img_combo = ttk.Combobox(
            self.root,
            values=list(self.img_path_dict.keys()),
            state="readonly",
            font=("微软雅黑", 12),
            width=15
        )
        self.img_combo.pack(pady=5)
        self.img_combo.current(0)
        self.img_combo.bind("<<ComboboxSelected>>", self.img_combo_on_select)

        self.img_label = tk.Label(self.root, text="请选择清晰度", bg="white", relief="sunken")
        self.img_label.pack(pady=20, padx=40, fill="both", expand=True)

        # 程序启动时显示默认图片
        self.img_combo_on_select()

    def run(self):
        self.create_widgets()

    # 程序关闭时确保释放摄像头
    def on_closing(self):
        self.stop_camera()
        self.root.destroy()


if __name__ == '__main__':
    print("hello Sparky")
    window = tk.Tk()
    app = ShowSparky(window)
    app.run()
    window.protocol("WM_DELETE_WINDOW", app.on_closing)  # 重要！关闭窗口时释放摄像头
    window.mainloop()
