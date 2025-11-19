import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import cv2


def open_img(img_path):
    img = None
    try:
        img = Image.open(img_path)
    except Exception as e:
        messagebox.showerror(f"图片路径错误:{e}")
    return img


class ShowSparky:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sparky")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.img_path_dict = {}

        # 图片清晰度选择按钮
        self.img_combo = None
        # 图片显示区域
        self.img_label = None
        self.photo = None

    def update_img_label(self, img):
        img.thumbnail((550, 400))  # 限制最大尺寸
        self.photo = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.photo, text="")

    def show_4k(self):
        img = Image.Image()
        try:
            # 调用摄像头
            cap = cv2.VideoCapture(0)
            # 检查摄像头是否成功打开
            if not cap.isOpened():
                print("错误：无法打开摄像头！检查是否被占用或驱动是否正常")
            paused = False

            while True:
                if not paused:
                    ret, frame = cap.read()  # 读取一帧
                    if not ret:
                        print("无法读取画面（摄像头断开？）")
                        break

                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.update_img_label(img)

                # 键盘响应
                key = cv2.waitKey(1) & 0xFF  # 每1ms检查一次按键

                if key == ord('q'):  # 按 q 退出
                    break
                elif key == ord('s'):  # 按 s 截图保存到当前目录
                    filename = f"../4K.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"截图已保存：{filename}")
                elif key == ord(' '):  # 按空格暂停/继续
                    paused = not paused
                    print("暂停" if paused else "继续")

            # 释放资源
            cap.release()
            cv2.destroyAllWindows()
            print("摄像头已关闭")

        except Exception as e:
            messagebox.showerror(f"<UNK>:{e}")
        finally:
            img.thumbnail((550, 400))  # 限制最大尺寸
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.photo, text="")

    def img_combo_on_select(self, event=None):
        selected = self.img_combo.get()
        if selected == "4K":
            self.show_4k()
            pass
        img_path = self.img_path_dict[selected]
        img = open_img(img_path)
        self.update_img_label(img)
        return img

    def create_widgets(self):
        self.img_path_dict = {
            "360P": "../img/360.jpg",
            "480P": "../img/480.jpg",
            "1080P": "../img/1080.jpg",
            "4K": ""
        }

        img_combo_options = list(self.img_path_dict.keys())
        self.img_combo = ttk.Combobox(
            self.root, values=img_combo_options, state="readonly",
        )
        self.img_combo.pack()
        self.img_combo.current(0)
        self.img_combo.bind("<<ComboboxSelected>>", self.img_combo_on_select)  # 绑定选中事件

        # === 图片显示区域 ===
        self.img_label = tk.Label(
            self.root, text="未选择图片", bg="white", width=600, height=600,
            relief="sunken", anchor="center")
        self.img_label.pack(pady=10, padx=20, fill="both", expand=False)

    def run(self):
        self.create_widgets()
        self.img_combo_on_select(None)


if __name__ == '__main__':
    print("hello Sparky")
    window = tk.Tk()
    sparky = ShowSparky(window)
    sparky.run()
    window.mainloop()
