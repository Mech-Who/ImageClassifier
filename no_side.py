import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import shutil
from collections import deque


class Command:
    """命令基类"""

    def execute(self):
        pass

    def undo(self):
        pass


class MoveImageCommand(Command):
    """移动图片命令"""

    def __init__(self, app, is_similar, filename):
        self.app = app
        self.is_similar = is_similar
        self.filename = filename
        self.src_path = os.path.join(app.current_dir, filename)
        self.target_dir = app.similar_dir if is_similar else app.dissimilar_dir
        self.dest_path = os.path.join(self.target_dir, filename)

    def execute(self):
        os.makedirs(self.target_dir, exist_ok=True)
        shutil.move(self.src_path, self.dest_path)
        self.app.image_files.remove(self.filename)

    def undo(self):
        shutil.move(self.dest_path, self.src_path)
        self.app.image_files.append(self.filename)
        self.app.image_files.sort()


class CommandQueue:
    """命令队列"""

    def __init__(self, max_length=3):
        self.queue = deque(maxlen=max_length)

    def add_command(self, command):
        if len(self.queue) == self.queue.maxlen:
            self.queue.popleft().execute()
        self.queue.append(command)

    def execute_all(self):
        while self.queue:
            self.queue.popleft().execute()

    def undo_last(self) -> bool:
        if self.queue:
            self.queue.pop()
            return True
        return False

    def get_commands(self):
        return list(self.queue)


class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片分类工具")
        self.root.geometry("900x700")

        # 状态变量
        self.image_files = []
        self.current_index = -1
        self.current_dir = ""
        self.similar_dir = ""
        self.dissimilar_dir = ""

        # 命令队列
        self.command_queue = CommandQueue()

        # 创建UI控件
        self.create_widgets()

        # 绑定键盘事件
        self.root.bind("<Left>", lambda event: self.prev_image())
        self.root.bind("<Right>", lambda event: self.next_image())
        self.root.bind("<s>", lambda event: self.add_move_command(True))
        self.root.bind("<d>", lambda event: self.add_move_command(False))
        self.root.bind("<z>", lambda event: self.undo_last_command())
        self.root.bind("<c>", lambda event: self.clear_command_queue())

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """关闭程序时执行队列中的所有命令"""
        self.command_queue.execute_all()
        self.root.destroy()

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
            command=lambda: self.add_move_command(True),
        )
        self.similar_btn.pack(side=tk.LEFT, padx=10)

        self.dissimilar_btn = tk.Button(
            btn_frame,
            text="不相似",
            bg="#ffaaaa",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=lambda: self.add_move_command(False),
        )
        self.dissimilar_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="撤回", width=10, command=self.undo_last_command
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="清空队列", width=10, command=self.clear_command_queue
        ).pack(side=tk.LEFT, padx=10)  # 添加清空队列按钮

        tk.Button(btn_frame, text="下一张 →", width=10, command=self.next_image).pack(
            side=tk.RIGHT, padx=40
        )

        # 显示命令队列
        self.queue_var = tk.StringVar(value="队列: []")
        tk.Label(self.root, textvariable=self.queue_var, fg="blue").pack(pady=5)

    def update_queue_display(self):
        commands = [
            f"{cmd.filename} ({'相似' if cmd.is_similar else '不相似'})"
            for cmd in self.command_queue.get_commands()
        ]
        self.queue_var.set(f"队列: {commands}")

    def add_move_command(self, is_similar):
        if self.current_index < 0 or not self.image_files:
            return

        filename = self.image_files[self.current_index]
        command = MoveImageCommand(self, is_similar, filename)
        self.command_queue.add_command(command)

        # 更新图片显示
        self.current_index += 1
        if self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1
        self.show_current_image()

        # 更新队列显示
        self.update_queue_display()

    def undo_last_command(self):
        if self.command_queue.undo_last():
            self.current_index -= 1
        self.update_queue_display()
        self.show_current_image()

    # 添加清空队列的方法
    def clear_command_queue(self):
        self.command_queue.queue.clear()
        self.update_queue_display()

    def open_directory(self):
        # 执行队列中的所有命令
        self.command_queue.execute_all()

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
            self.image_label.config(image=None)
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

    def prev_image(self):
        if not self.image_files or self.current_index <= 0:
            return
        self.current_index -= 1
        self.show_current_image()

    def next_image(self):
        if not self.image_files or self.current_index >= len(self.image_files) - 1:
            return
        self.current_index += 1
        self.show_current_image()

    def update_buttons_state(self, state):
        self.similar_btn.config(state=state)
        self.dissimilar_btn.config(state=state)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
