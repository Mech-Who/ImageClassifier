import os
import shutil
import tkinter as tk
from pathlib import Path
from collections import deque
from abc import abstractmethod
from tkinter import filedialog
from PIL import Image, ImageTk
from loguru import logger


class Command:
    @abstractmethod
    def execute(): ...
    @abstractmethod
    def undo(): ...


class MoveCommand(Command):
    def __init__(self, filename: str, src_dir: str, dst_dir: str, is_similar: bool):
        super().__init__()
        self.filename = filename
        self.is_similar = is_similar
        self.src_dir = Path(src_dir)
        self.dst_dir = Path(dst_dir)

    def execute(self):
        logger.debug(f"execute: {self.filename}(sim-{self.is_similar})")
        if not self.dst_dir.exists():
            self.dst_dir.mkdir(parents=True, exist_ok=True)
        src_path = self.src_dir / self.filename
        dst_path = self.dst_dir / self.filename
        try:
            shutil.move(str(src_path), str(dst_path))
        except Exception as e:
            print(f"移动文件失败: {e}")

    def undo(self):
        if not self.src_dir.exists():
            self.src_dir.mkdir(parents=True, exist_ok=True)
        src_path = self.src_dir / self.filename
        dst_path = self.dst_dir / self.filename
        shutil.move(str(dst_path), str(src_path))
        raise NotImplementedError("Move Commad `undo()` not implement!")


class ImageClassifierApp:
    def __init__(self, root, max_buffer: int = 3):
        self.root = root
        self.max_buffer = max_buffer
        # Basic Info
        self.root.title("图片分类工具")
        self.root.geometry("900x700")

        # Bind Keyboard Event
        self.root.bind("<s>", lambda event: self.move_image(True))  # 绑定 S 键
        self.root.bind("<d>", lambda event: self.move_image(False))  # 绑定 D 键
        self.root.bind("<z>", lambda event: self.undo_command())  # 绑定 Z 键
        self.root.bind("<c>", lambda event: self.clear_queue())  # 绑定 C 键
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # State Variables
        self.image_files = deque()
        self.current_image = None
        self.current_dir = None
        self.similar_dir = None
        self.dissimilar_dir = None
        self.command_queue = deque(maxlen=max_buffer)

        # Create UI Widgets
        self.create_widgets()

    def create_widgets(self) -> None:
        # Top Frame
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)
        ## Button
        tk.Button(top_frame, text="打开文件夹", command=self.open_directory).pack(
            side=tk.LEFT, padx=5
        )
        ## Status Text
        self.status_text = tk.StringVar()
        tk.Label(top_frame, textvariable=self.status_text, fg="gray").pack(
            side=tk.RIGHT, padx=10
        )

        # Middle Frame
        ## Image canvas
        self.img_frame = tk.Frame(self.root, bg="#f0f0f0", height=500)
        self.img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ## Image Name
        self.image_name = tk.StringVar()
        tk.Label(self.img_frame, textvariable=self.image_name, fg="gray").pack(
            side=tk.TOP, padx=10
        )
        ## Image Canvas
        self.image_canvas = tk.Label(self.img_frame)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # Bottom Button Frame
        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack(fill=tk.X)
        ## Similar Button
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
        ## Dissimilar Button
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
        ## Undo Button
        self.undo_btn = tk.Button(
            btn_frame,
            text="撤回",
            bg="#d1c9c9",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=lambda: self.undo_command(),
        )
        self.undo_btn.pack(side=tk.RIGHT, padx=10)
        ## Clear Queue Button
        self.clear_queue_btn = tk.Button(
            btn_frame,
            text="清空队列",
            bg="#f85c5c",
            width=10,
            height=2,
            state=tk.DISABLED,
            command=lambda: self.clear_queue(),
        )
        self.clear_queue_btn.pack(side=tk.RIGHT, padx=10)

        # Bottom Frame
        bottom_frame = tk.Frame(self.root, pady=15)
        bottom_frame.pack(fill=tk.X)
        ## Queue Text
        self.queue_text = tk.StringVar()
        tk.Label(bottom_frame, textvariable=self.queue_text, fg="gray").pack(
            side=tk.BOTTOM, padx=10
        )

    def on_close(self) -> None:
        self.clear_queue()
        self.root.destroy()

    # Button Event
    def open_directory(self) -> None:
        directory = filedialog.askdirectory(title="选择图片文件夹")
        if not directory:
            return

        directory = Path(directory)
        self.current_dir = directory
        self.similar_dir = directory / "相似"
        self.dissimilar_dir = directory / "不相似"

        # 获取所有支持的图片文件
        all_images = [
            f
            for f in os.listdir(directory)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]
        all_images.sort()
        self.image_files.extend(all_images)

        if len(self.image_files) == 0:
            self.status_text.set("目录中没有找到图片文件")
            return

        self.update_buttons_state(tk.NORMAL)

        self.current_image = self.image_files.popleft()
        self.show_current_image()

    def move_image(self, is_similar):
        if self.current_image is None:
            return

        # 创建目录（如果需要）
        target_dir = self.similar_dir if is_similar else self.dissimilar_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        # 移动文件
        command = MoveCommand(
            filename=self.current_image,
            src_dir=str(self.current_dir),
            dst_dir=str(target_dir),
            is_similar=is_similar,
        )
        if len(self.command_queue) == self.max_buffer:
            pop_command = self.command_queue.popleft()
            pop_command.execute()
        self.command_queue.append(command)

        # 更新列表和索引
        if len(self.image_files) > 0:
            self.current_image = self.image_files.popleft()
        else:
            self.current_image = None
            self.update_buttons_state(tk.DISABLED)
            self.image_canvas.config(image=None)
            self.status_text.set(f"分类完毕! {str(self.current_dir)}")
        self.show_current_image()

    def undo_command(self):
        if len(self.command_queue) <= 0:
            return
        command = self.command_queue.pop()
        self.image_files.appendleft(self.current_image)
        self.current_image = command.filename
        self.show_current_image()

    def clear_queue(self):
        if len(self.command_queue) <= 0:
            return
        while len(self.command_queue) > 0:
            command = self.command_queue.pop()
            command.execute()
        self.show_current_image()

    # Operations
    def show_current_image(self):
        logger.debug("===== [show current] =====")
        logger.debug(f"img_files={list(self.image_files)[:5]}")
        msg = ",".join(
            [f"{com.filename}(sim-{com.is_similar})" for com in self.command_queue]
        )
        logger.debug(f"queue=[{msg}]")
        logger.debug(f"current_image={self.current_image}")
        if self.current_image is None:
            return
        # Queue Text
        if len(self.command_queue) > 0:
            queue_texts = [
                f"{item.filename}({'相似' if item.is_similar else '不相似'})"
                for item in self.command_queue
            ]
            self.queue_text.set(f"[{','.join(queue_texts)}]")
        else:
            self.queue_text.set("[]")
        # Image Name
        self.image_name.set(self.current_image)
        img_path = self.current_dir / self.current_image
        try:
            # 加载图片并调整大小
            img = Image.open(str(img_path))

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
            self.image_canvas.config(image=photo)
            self.image_canvas.image = photo

        except Exception as e:
            logger.exception(f"Error loading image: {e}")
        # 更新状态
        total_image = len(self.image_files)
        if self.current_image:
            total_image += 1
        self.status_text.set(f"{total_image}: {self.current_dir.name}")

    def update_buttons_state(self, state):
        self.similar_btn.config(state=state)
        self.dissimilar_btn.config(state=state)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
