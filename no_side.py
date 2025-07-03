import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import shutil


class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片分类工具")
        self.root.geometry("900x700")

        # 绑定键盘事件
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<s>", lambda event: self.move_image(True))  # 绑定 S 键
        self.root.bind("<d>", lambda event: self.move_image(False))  # 绑定 D 键

        # 状态变量
        self.image_files = []
        self.current_index = -1
        self.current_dir = ""
        self.similar_dir = ""
        self.dissimilar_dir = ""

        # 创建UI控件
        self.create_widgets()

        # 绑定键盘事件
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)

    def create_widgets(self):
        # 顶部操作区域
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Button(top_frame, text="打开文件夹", command=self.open_directory).pack(
            side=tk.LEFT, padx=5
        )

        self.status_var = tk.StringVar()
        tk.Label(top_frame, textvariable=self.status_var, fg="gray").pack(
            side=tk.RIGHT, padx=10
        )

        # 图片显示区域
        self.img_frame = tk.Frame(self.root, bg="#f0f0f0", height=500)
        self.img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.image_label = tk.Label(self.img_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 底部按钮区域
        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="← 上一张", width=10, command=self.prev_image).pack(
            side=tk.LEFT, padx=40
        )

        self.similar_btn = tk.Button(
            btn_frame,
            text="相似",
            bg="#aaffaa",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=lambda: self.move_image(True),
        )
        self.similar_btn.pack(side=tk.LEFT, padx=10)

        self.dissimilar_btn = tk.Button(
            btn_frame,
            text="不相似",
            bg="#ffaaaa",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=lambda: self.move_image(False),
        )
        self.dissimilar_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="下一张 →", width=10, command=self.next_image).pack(
            side=tk.RIGHT, padx=40
        )

    def open_directory(self):
        directory = filedialog.askdirectory(title="选择图片文件夹")
        if not directory:
            return

        self.current_dir = directory
        self.similar_dir = os.path.join(directory, "相似")
        self.dissimilar_dir = os.path.join(directory, "不相似")

        # 获取所有支持的图片文件
        self.image_files = [
            f
            for f in os.listdir(directory)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]
        self.image_files.sort()

        if not self.image_files:
            self.status_var.set("目录中没有找到图片文件")
            return

        self.current_index = 0
        self.update_buttons_state(tk.NORMAL)
        self.show_current_image()

    def show_current_image(self):
        if not self.image_files or self.current_index < 0:
            return

        img_path = os.path.join(self.current_dir, self.image_files[self.current_index])
        try:
            # 加载图片并调整大小
            img = Image.open(img_path)

            # 获取窗口的宽高
            window_width = self.img_frame.winfo_width()
            window_height = self.img_frame.winfo_height()

            # 调整图片大小以适应窗口
            img_ratio = img.size[0] / img.size[1]
            window_ratio = window_width / window_height

            if img_ratio > window_ratio:
                new_width = window_width
                new_height = int(new_width / img_ratio)
            else:
                new_height = window_height
                new_width = int(new_height * img_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 显示图片
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo

            # 更新状态
            self.status_var.set(
                f"{self.current_index + 1}/{len(self.image_files)}: "
                f"{self.image_files[self.current_index]} "
                f"({img.size[0]}×{img.size[1]})"
            )
        except Exception as e:
            print(f"Error loading image: {e}")

    def prev_image(self, event=None):
        if not self.image_files or self.current_index <= 0:
            return
        self.current_index -= 1
        self.show_current_image()

    def next_image(self, event=None):
        if not self.image_files or self.current_index >= len(self.image_files) - 1:
            return
        self.current_index += 1
        self.show_current_image()

    def move_image(self, is_similar):
        if self.current_index < 0 or not self.image_files:
            return

        # 创建目录（如果需要）
        target_dir = self.similar_dir if is_similar else self.dissimilar_dir
        os.makedirs(target_dir, exist_ok=True)

        # 移动文件
        filename = self.image_files[self.current_index]
        src_path = os.path.join(self.current_dir, filename)
        dest_path = os.path.join(target_dir, filename)

        try:
            shutil.move(src_path, dest_path)

            # 更新列表和索引
            del self.image_files[self.current_index]
            if not self.image_files:
                self.current_index = -1
                self.update_buttons_state(tk.DISABLED)
                self.image_label.config(image=None)
                self.status_var.set("已完成所有图片分类!")
            else:
                if self.current_index >= len(self.image_files):
                    self.current_index = len(self.image_files) - 1
                self.show_current_image()
        except Exception as e:
            print(f"移动文件失败: {e}")

    def update_buttons_state(self, state):
        self.similar_btn.config(state=state)
        self.dissimilar_btn.config(state=state)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
