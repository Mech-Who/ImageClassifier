import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import shutil
import threading
import time


class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片分类工具")
        self.root.geometry("1200x700")

        # 状态变量
        self.image_files = []
        self.current_index = -1
        self.current_dir = ""
        self.similar_dir = ""
        self.dissimilar_dir = ""
        self.tree_root_path = ""
        self.file_tree_items = {}  # 存储Treeview节点ID与路径的映射

        # 创建UI布局框架
        self.create_layout()

        # 绑定键盘事件
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)

        # 监控线程标志
        self.monitor_running = False
        self.monitor_thread = None

    def create_layout(self):
        # 主框架（分隔为左右两部分）
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧面板（目录树）
        self.left_panel = tk.Frame(main_frame, width=250)
        main_frame.add(self.left_panel, minsize=200)
        self.create_treeview()

        # 右侧面板（图片查看）
        self.right_panel = tk.Frame(main_frame)
        main_frame.add(self.right_panel, minsize=600)
        self.create_image_viewer()

    def create_treeview(self):
        # 树视图框架
        tree_frame = tk.Frame(self.left_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 树视图组件
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # 设置树视图列
        self.tree["columns"] = ("1", "2")
        self.tree.column("#0", width=200, minwidth=150, anchor=tk.W)
        self.tree.column("1", width=50, minwidth=50, anchor=tk.CENTER)
        self.tree.column("2", width=30, minwidth=30, anchor=tk.CENTER)

        # 定义列标题
        self.tree.heading("#0", text="目录结构", anchor=tk.W)
        self.tree.heading("1", text="类型", anchor=tk.CENTER)
        self.tree.heading("2", text="项目数", anchor=tk.CENTER)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 工具栏
        toolbar = tk.Frame(self.left_panel)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(toolbar, text="刷新目录", command=self.refresh_treeview).pack(
            side=tk.LEFT
        )
        tk.Button(toolbar, text="打开文件夹", command=self.open_directory).pack(
            side=tk.RIGHT
        )

    def create_image_viewer(self):
        # 顶部操作区域
        top_frame = tk.Frame(self.right_panel, pady=10)
        top_frame.pack(fill=tk.X)

        self.path_label = tk.Label(top_frame, text="当前目录：未选择")
        self.path_label.pack(side=tk.LEFT, padx=5, anchor=tk.W)

        self.status_var = tk.StringVar()
        tk.Label(top_frame, textvariable=self.status_var, fg="gray").pack(
            side=tk.RIGHT, padx=10
        )

        # 图片显示区域
        self.img_frame = tk.Frame(self.right_panel, bg="#f0f0f0", height=500)
        self.img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.image_label = tk.Label(self.img_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 底部按钮区域
        btn_frame = tk.Frame(self.right_panel, pady=15)
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

    def build_treeview(self, path):
        """构建目录树结构"""
        # 清空现有树
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_tree_items.clear()

        if not path:
            return

        self.tree_root_path = path

        # 添加根节点
        root_item = self.tree.insert(
            "",
            "end",
            text=os.path.basename(path),
            values=("目录", ""),
            open=True,
            tags=("root",),
        )
        self.file_tree_items[root_item] = path

        # 递归添加子节点
        self.add_tree_nodes(root_item, path)

        # 启动目录监控线程
        self.start_directory_monitor(path)

    def add_tree_nodes(self, parent_id, parent_path):
        """递归添加目录和文件到树视图"""
        try:
            # 添加目录节点
            for item in sorted(os.listdir(parent_path)):
                item_path = os.path.join(parent_path, item)
                if os.path.isdir(item_path) and not item.startswith("."):
                    # 计算目录中的项目数量
                    item_count = len(os.listdir(item_path))
                    item_id = self.tree.insert(
                        parent_id,
                        "end",
                        text=item,
                        values=("目录", f"{item_count}"),
                        tags=("folder",),
                    )
                    self.file_tree_items[item_id] = item_path
                    # 递归处理子目录
                    self.add_tree_nodes(item_id, item_path)

            # 添加图片文件节点（仅限顶级目录）
            for item in sorted(os.listdir(parent_path)):
                item_path = os.path.join(parent_path, item)
                if os.path.isfile(item_path) and item.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".bmp")
                ):
                    self.tree.insert(
                        parent_id,
                        "end",
                        text=item,
                        values=("图片", ""),
                        tags=("image",),
                    )

        except PermissionError:
            # 处理可能遇到的权限问题
            pass

    def start_directory_monitor(self, path):
        """启动目录监控线程"""
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1)

        self.monitor_running = True
        self.monitor_thread = threading.Thread(
            target=self.monitor_directory_changes, args=(path,), daemon=True
        )
        self.monitor_thread.start()

    def monitor_directory_changes(self, path):
        """监控目录变化并更新树视图"""
        last_state = {}

        # 初始快照
        for root, dirs, files in os.walk(path):
            for name in dirs + files:
                item_path = os.path.join(root, name)
                last_state[item_path] = os.path.getmtime(item_path)

        while self.monitor_running:
            time.sleep(1)  # 每1秒检查一次

            changed = False
            new_state = {}

            # 获取新快照
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    item_path = os.path.join(root, name)
                    try:
                        mtime = os.path.getmtime(item_path)
                        new_state[item_path] = mtime

                        # 如果文件新创建或修改
                        if (
                            item_path not in last_state
                            or last_state[item_path] != mtime
                        ):
                            changed = True
                    except FileNotFoundError:
                        # 文件可能被删除
                        changed = True

            # 检查删除的文件
            for item_path in list(last_state.keys()):
                if item_path not in new_state:
                    changed = True
                    break

            if changed:
                last_state = new_state
                # 在UI线程中更新树视图
                self.root.after(0, self.refresh_treeview)

            # 检查是否继续运行
            if not self.monitor_running:
                break

    def refresh_treeview(self):
        """刷新目录树视图"""
        if self.tree_root_path and os.path.exists(self.tree_root_path):
            self.build_treeview(self.tree_root_path)

    def on_tree_select(self, event):
        """处理目录树的选择事件"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        selected_id = selected_items[0]
        path = self.file_tree_items.get(selected_id)

        if path and os.path.isdir(path):
            # 用户选择了目录，加载其中的图片
            self.load_images_from_directory(path)
        elif path and os.path.isfile(path):
            # 用户选择了文件，直接显示该文件
            file_dir = os.path.dirname(path)
            filename = os.path.basename(path)

            if file_dir != self.current_dir:
                self.load_images_from_directory(file_dir)

            # 在文件列表中定位选中的文件
            if filename in self.image_files:
                self.current_index = self.image_files.index(filename)
                self.show_current_image()

    def load_images_from_directory(self, directory):
        """从目录加载图片"""
        if not directory:
            return

        self.current_dir = directory
        self.similar_dir = os.path.join(directory, "相似")
        self.dissimilar_dir = os.path.join(directory, "不相似")
        self.path_label.config(text=f"当前目录：{directory}")

        # 获取所有支持的图片文件
        self.image_files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
            and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]
        self.image_files.sort()

        if not self.image_files:
            self.status_var.set("目录中没有找到图片文件")
            self.update_buttons_state(tk.DISABLED)
            self.image_label.config(image=None)
            return

        self.current_index = 0
        self.update_buttons_state(tk.NORMAL)
        self.show_current_image()

    def open_directory(self):
        """打开目录并构建目录树"""
        directory = filedialog.askdirectory(title="选择图片文件夹")
        if not directory:
            return

        self.build_treeview(directory)
        self.load_images_from_directory(directory)

    def show_current_image(self):
        if not self.image_files or self.current_index < 0:
            return

        img_path = os.path.join(self.current_dir, self.image_files[self.current_index])
        try:
            # 加载图片并调整大小
            img = Image.open(img_path)
            width, height = img.size
            max_size = 800
            if max(width, height) > max_size:
                ratio = max_size / max(width, height)
                img = img.resize(
                    (int(width * ratio), int(height * ratio)), Image.LANCZOS
                )

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

        # 更新目录树
        self.refresh_treeview()

    def update_buttons_state(self, state):
        self.similar_btn.config(state=state)
        self.dissimilar_btn.config(state=state)

    def __del__(self):
        # 停止监控线程
        self.monitor_running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
