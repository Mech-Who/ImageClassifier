import json
import pandas as pd
from classifier import FLORIDA_CATE


def json_to_excel(json_file, output_file):
    """
    将 JSON 数据转换为 Excel 表格。
    :param json_file: JSON 文件路径
    :param output_file: 输出 Excel 文件路径
    """
    # 读取 JSON 数据
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 创建一个空的 DataFrame
    rows = []
    # 遍历数据集
    for dataset_name, dataset_info in data["datasets"].items():
        if dataset_name == "弗罗里达generated":
            for category_name, category_info in dataset_info["categories"].items():
                cate_idx = int(category_name.split("_")[-1])
                rows.append(
                    {
                        "数据集": dataset_name,
                        "类别": cate_idx,
                        "相似数量": category_info["similar"],
                        "不相似数量": category_info["dissimilar"],
                        "总数量": category_info["total"],
                        "相似比例": category_info["ratio"],
                        "类别名称": FLORIDA_CATE[cate_idx],
                    }
                )
        else:
            pudu_rows = {}
            for sim_name, sim_info in dataset_info["categories"].items():
                for category_name, category_info in sim_info["categories"].items():
                    cates = category_name.split("_")
                    cate_name = cates[-1]
                    cate_idx = int(cates[-2])
                    dic = pudu_rows.get(
                        category_name,
                        {
                            "数据集": dataset_name,
                            "类别": cate_idx,
                            "相似数量": 0,
                            "不相似数量": 0,
                            "总数量": 0,
                            "相似比例": 0.0,
                            "类别名称": cate_name,
                        },
                    )
                    dic["数据集"] = dataset_name
                    dic["相似数量"] += category_info["similar"]
                    dic["不相似数量"] += category_info["dissimilar"]
                    dic["总数量"] += category_info["total"]
                    dic["相似比例"] = (
                        dic["相似数量"] / dic["总数量"] if dic["总数量"] > 0 else 0
                    )
                    pudu_rows[category_name] = dic

            for value in pudu_rows.values():
                rows.append(value)
        # 添加总的比例信息
        total_row = {
            "数据集": dataset_name,
            "类别": 1000,
            "相似数量": dataset_info["similar"],
            "不相似数量": dataset_info["dissimilar"],
            "总数量": dataset_info["total"],
            "相似比例": dataset_info["similar_ratio"],
            "类别名称": "",
        }
        rows.append(total_row)
        # dataset_df = pd.DataFrame(rows)
        # dataset_df.sort_values(by="类别", ascending=True, inplace=True)

    df = pd.DataFrame(rows)
    df.sort_values(by=["数据集", "类别"], ascending=[True, True], inplace=True)
    df.loc[df["类别"] == 1000, "数据集"] = "总计"

    # 保存为 Excel 文件
    df.to_excel(output_file, index=False)
    print(f"数据已保存到 {output_file}")


if __name__ == "__main__":
    base_directory = r"G:\南科大可视化图片（普渡_弗罗里达）筛选"
    # JSON 文件路径
    json_file_path = rf"{base_directory}\statistics.json"
    # 输出 Excel 文件路径
    output_excel_path = rf"{base_directory}\statistics.xlsx"

    # 转换并保存
    json_to_excel(json_file_path, output_excel_path)
