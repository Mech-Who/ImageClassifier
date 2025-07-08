import os
from pathlib import Path
from loguru import logger

ORIGIN_CATEGORIES = {
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

ORIGIN_CLASS_INDEX = {value: key for key, value in ORIGIN_CATEGORIES.items()}

# 标签信息
CORRECT_CATEGORIES = {
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
    # start
    15: "electric guitar",
    16: "electric locomotive",
    17: "espresso maker",
    18: "folding chair",
    19: "golf ball",
    20: "grand piano",
    21: "iron",
    22: "jack-o-lantern",
    23: "mailbag",
    24: "missile",
    25: "mitten",
    26: "mountain bike",
    27: "mountain tent",
    28: "pajama",
    29: "parachute",
    30: "pool table",
    31: "radio telescope",
    32: "reflex camera",
    33: "revolver",
    34: "running shoe",
    35: "watch",
    # finish
    36: "banana",
    37: "pizza",
    38: "daisy",
    39: "bolete",
}

CORRECT_CLASS_INDEX = {value: key for key, value in CORRECT_CATEGORIES.items()}


def rename_pudu_directories(base_dir):
    """
    重命名目录为 label_{index}_{class name}[({wrong class name})] 的形式。
    :param base_dir: 根目录路径
    """
    base_dir = Path(base_dir)
    # sim
    for sim_dir in os.listdir(str(base_dir)):
        sim_path = base_dir / sim_dir
        # only dir
        if not sim_path.is_dir():
            continue
        for label_dir in os.listdir(str(sim_path)):
            label_path = sim_path / label_dir
            # only dir
            if not label_path.is_dir():
                continue

            # 提取标签索引
            class_idx = ORIGIN_CLASS_INDEX[label_dir]
            correct_label = CORRECT_CATEGORIES[class_idx]
            new_dirname = f"label_{class_idx}_{correct_label}"
            if correct_label != label_dir:
                new_dirname += f"({label_dir})"

            # 重命名目录
            new_label_path = base_dir / sim_dir / new_dirname
            try:
                os.rename(str(label_path), str(new_label_path))
                logger.info(f"重命名: {label_dir} -> {new_dirname}")
            except Exception as e:
                logger.error(f"重命名失败: {label_dir} -> {new_dirname}, 错误: {e}")


if __name__ == "__main__":
    import sys

    logger.remove()
    logger.add(sys.stdout, level="INFO", colorize=True)
    logger.add("logs/rename_class.log", level="INFO", colorize=False)
    # 使用示例
    base_directory = r"G:\南科大可视化图片（普渡_弗罗里达）\普渡_generated - 副本"
    rename_pudu_directories(base_directory)
