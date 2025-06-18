import os
import re
import shutil
import argparse

# 定义类别名称映射表
CATEGORIES = {
    0: "German shepherd",
    1: "Egyptian cat",
    2: "lycaenid",
    3: "sorrel",
    4: "capuchin",
    5: "African elephant",
    6: "giant panda",
    7: "anemone fish",
    8: "airliner",
    9: "broom",
    10: "canoe",
    11: "cellular telephone",
    12: "coffee mug",
    13: "convertible",
    14: "desktop computer",
    15: "watch",
    16: "electric guitar",
    17: "electric locomotive",
    18: "espresso maker",
    19: "folding chair",
    20: "golf ball",
    21: "grand piano",
    22: "iron",
    23: "jack-o-lantern",
    24: "mailbag",
    25: "missile",
    26: "mitten",
    27: "mountain bike",
    28: "mountain tent",
    29: "pajama",
    30: "parachute",
    31: "pool table",
    32: "radio telescope",
    33: "reflex camera",
    34: "revolver",
    35: "running shoe",
    36: "banana",
    37: "pizza",
    38: "daisy",
    39: "bolete",
}


def organize_images(input_dir, move_files=False):
    """
    根据文件名中的类别编号整理图像文件

    参数:
    input_dir (str): 包含图像的源目录路径
    move_files (bool): True表示移动文件，False表示复制文件
    """
    # 验证目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误：目录 '{input_dir}' 不存在")
        return

    # 处理文件的操作函数
    file_operation = shutil.move if move_files else shutil.copy2

    processed = 0
    # 遍历目录中的文件
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)

        # 跳过目录
        if not os.path.isfile(filepath):
            continue

        # 提取类别编号
        match = re.match(r'.*_(\d+)_sim.*', filename)
        if not match:
            print(f"警告：文件 '{filename}' 不符合命名规则，跳过")
            continue

        try:
            category_id = int(match.group(1))
            # 验证类别ID范围
            if category_id not in CATEGORIES:
                print(f"警告：无效类别ID {category_id}，文件 '{filename}' 跳过")
                continue

            category_name = CATEGORIES[category_id]
            target_dir = os.path.join(input_dir, category_name)

            # 创建类别目录
            os.makedirs(target_dir, exist_ok=True)

            # 移动/复制文件
            file_operation(filepath, os.path.join(target_dir, filename))
            processed += 1

        except (ValueError, TypeError):
            print(f"警告：无法解析 '{filename}' 中的类别编号")

    print(f"操作完成！处理文件数: {processed}")
    print(f"模式: {'移动' if move_files else '复制'}文件")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根据文件名中的类别编号整理图像")
    parser.add_argument("directory", help="包含图像的目录路径")
    parser.add_argument(
        "-m", "--move", action="store_true", help="移动文件而非复制文件（默认是复制）"
    )

    args = parser.parse_args()
    organize_images(args.directory, move_files=args.move)
