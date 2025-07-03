import os
import re
import shutil
import argparse

# 定义类别名称映射表
CATEGORIES = {
    0: "German shepherd",  # 德国牧羊犬
    1: "Egyptian cat",  # 缅甸猫
    2: "lycaenid",  # 灰蝶
    3: "sorrel",  # 栗色马
    4: "capuchin",  # 金丝猴
    5: "African elephant",  # 非洲大象
    6: "giant panda",  # 大熊猫
    7: "anemone fish",  # 小丑鱼
    8: "airliner",  # 客机
    9: "broom",  # 扫帚
    10: "canoe",  # 独木舟
    11: "cellular telephone",  # 蜂巢电话
    12: "coffee mug",  # 咖啡杯
    13: "convertible",  # 敞篷车
    14: "desktop computer",  # 台式计算机
    15: "watch",  # 手表 -> 电吉他 electric guitar
    16: "electric guitar",  # 电吉他 -> 电力机车 electric locomotive
    17: "electric locomotive",  #  电力机车 -> 浓缩咖啡机 espresso maker
    18: "espresso maker",  # 浓缩咖啡机 -> 折叠椅 folding chair
    19: "folding chair",  # 折叠椅 -> 高尔夫球 golf ball
    20: "golf ball",  # 高尔夫球 -> 钢琴 grand piano
    21: "grand piano",  # 钢琴 -> 熨斗 iron
    22: "iron",  # 熨斗 -> 南瓜灯 jack-o-lantern
    23: "jack-o-lantern",  # 南瓜灯 -> 邮袋 mailbag
    24: "mailbag",  # 邮袋 -> 导弹 missile
    25: "missile",  # 导弹 -> 手套 mitten
    26: "mitten",  # 手套 -> 山地自行车 mountain bike
    27: "mountain bike",  # 山地自行车 -> 山地帐篷 mountain tent
    28: "mountain tent",  # 山地帐篷 -> 睡衣 pajama
    29: "pajama",  # 睡衣 ->  降落伞 parachute
    30: "parachute",  # 降落伞 -> 台球桌 pool table
    31: "pool table",  # 台球桌 ->  射电望远镜 radio telescope
    32: "radio telescope",  # 射电望远镜 -> 反光照相机 reflex camera
    33: "reflex camera",  # 反光照相机 -> 左轮手枪 revolver
    34: "revolver",  # 左轮手枪 -> 跑步鞋 pajrunning shoeama
    35: "running shoe",  # 跑步鞋 -> 手表 watch
    36: "banana",  # 香蕉
    37: "pizza",  # 披萨
    38: "daisy",  # 雏菊
    39: "bolete",  # 牛肝菌
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
        match = re.match(r".*_(\d+)_sim.*", filename)
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
    """
    使用说明：
        对于给定目录中的文件进行分类，按照sim前的数字编号划分到对应的类中。可以通过move参数指定以移动或者复制的形式对文件进行分类。
        示例：`uv run classifier.py "G:/path/to/images/folder" -m` 表示以移动的方式将"G:/path/to/images/folder"目录下的文件进行分类
    作者：胡舒涵
    历史记录：
    2025-06-18  胡舒涵  创建脚本。
    """
    parser = argparse.ArgumentParser(description="根据文件名中的类别编号整理图像")
    parser.add_argument("directory", help="包含图像的目录路径")
    parser.add_argument(
        "-m", "--move", action="store_true", help="移动文件而非复制文件（默认是复制）"
    )

    args = parser.parse_args()
    organize_images(args.directory, move_files=args.move)
