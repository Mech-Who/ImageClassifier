import os
from pathlib import Path
from itertools import chain
from typing import Any
import pandas as pd


def iter_categories(
    base_dir: str, dataset: str, sim: str
) -> tuple[list, dict[str, Any]]:
    base_stats = {"similar": 0, "dissimilar": 0, "categories": {}}
    records = []
    base_dir = Path(base_dir)
    for category_name in os.listdir(str(base_dir)):
        category_path: Path = base_dir / category_name
        if not category_path.is_dir():
            continue

        similar_path: Path = category_path / "相似"
        dissimilar_path: Path = category_path / "不相似"

        similar_files = os.listdir(str(similar_path)) if similar_path.exists() else []
        dissimilar_files = (
            os.listdir(str(dissimilar_path)) if dissimilar_path.exists() else []
        )

        sim_len = len(similar_files)
        dis_len = len(dissimilar_files)

        base_stats["similar"] += sim_len
        base_stats["dissimilar"] += dis_len
        base_stats["categories"][category_name] = {
            "similar": sim_len,
            "dissimilar": dis_len,
            "total": sim_len + dis_len,
            "ratio": sim_len / (sim_len + dis_len) if (sim_len + dis_len) > 0 else 0,
        }

        # 记录详细信息
        cats = category_name.split("_")
        label_name = None
        if len(cats) > 2:
            label_name = "_".join(cats[:2])
        else:
            label_name = category_name
        for file_name in similar_files:
            records.append(
                {
                    "file_name": file_name,
                    "dataset": dataset,
                    "similarity_level": sim,
                    "category": label_name,
                    "similarity": "相似",
                }
            )
        for file_name in dissimilar_files:
            records.append(
                {
                    "file_name": file_name,
                    "dataset": dataset,
                    "similarity_level": sim,
                    "category": label_name,
                    "similarity": "不相似",
                }
            )
    base_stats["total"] = base_stats["similar"] + base_stats["dissimilar"]
    base_stats["similar_ratio"] = base_stats["similar"] / base_stats["total"]
    return records, base_stats


def count_images(base_dir):
    """
    统计数据集目录下的相似和不相似图片的数量以及比例。
    :param base_dir: 数据集根目录路径
    :return: 统计结果字典和详细记录列表
    """
    statistics = {"total_similar": 0, "total_dissimilar": 0, "datasets": {}}
    records = []  # 用于保存详细记录
    base_dir = Path(base_dir)

    for dataset_name in os.listdir(str(base_dir)):
        dataset_path = base_dir / dataset_name
        if not dataset_path.is_dir():
            continue

        dataset_stats = {"similar": 0, "dissimilar": 0, "categories": {}}

        # 检测是否存在相似度层级
        subfolders = os.listdir(str(dataset_path))
        if any(
            (dataset_path / subfolder).is_dir() and subfolder.startswith("sim")
            for subfolder in subfolders
        ):
            # 有相似度层级
            for sim_name in subfolders:
                sim_path = os.path.join(dataset_path, sim_name)
                if not os.path.isdir(sim_path):
                    continue

                recs, stats = iter_categories(sim_path, dataset_name, sim_name)
                records.extend(recs)
                dataset_stats["similar"] += stats["similar"]
                dataset_stats["dissimilar"] += stats["dissimilar"]
                dataset_stats["categories"][sim_name] = stats
        else:
            # 无相似度层级，直接处理类别目录
            recs, stats = iter_categories(str(dataset_path), dataset_name, "None")
            records.extend(recs)
            dataset_stats["similar"] += stats["similar"]
            dataset_stats["dissimilar"] += stats["dissimilar"]
            dataset_stats["categories"] = stats["categories"]

        dataset_stats["total"] = dataset_stats["similar"] + dataset_stats["dissimilar"]
        dataset_stats["similar_ratio"] = (
            dataset_stats["similar"] / dataset_stats["total"]
        )

        statistics["total_similar"] += dataset_stats["similar"]
        statistics["total_dissimilar"] += dataset_stats["dissimilar"]
        statistics["datasets"][dataset_name] = dataset_stats

    statistics["total"] = statistics["total_similar"] + statistics["total_dissimilar"]
    statistics["similar_ratio"] = (
        statistics["total_similar"] / statistics["total"]
        if statistics["total"] > 0
        else 0
    )
    statistics["dissimilar_ratio"] = (
        statistics["total_dissimilar"] / statistics["total"]
        if statistics["total"] > 0
        else 0
    )

    return statistics, records


def save_to_excel(records, output_path):
    """
    将记录保存为 Excel 文件。
    :param records: 记录列表
    :param output_path: 输出文件路径
    """
    df = pd.DataFrame(records)
    df.to_excel(output_path, index=False)
    print(f"统计结果已保存到 {output_path}")


if __name__ == "__main__":
    from pprint import pprint
    from json import dump

    # 替换为你的数据集根目录路径
    base_directory = r"D:\南科大可视化图片（普渡_弗罗里达）筛选"
    json_file = rf"{base_directory}\statistics.json"
    excel_file = rf"{base_directory}\image_data.xlsx"

    stats, records = count_images(base_directory)

    # 打印统计结果
    pprint(stats)

    # 保存到文件
    with open(json_file, "w", encoding="utf-8") as f:
        dump(stats, f, indent=2)
    save_to_excel(records, excel_file)
