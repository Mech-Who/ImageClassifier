import json
import pandas as pd


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
        if dataset_name == "弗罗里达":
            for category_name, category_info in dataset_info["categories"].items():
                rows.append(
                    {
                        "数据集": dataset_name,
                        "类别": category_name,
                        "相似数量": category_info["similar"],
                        "不相似数量": category_info["dissimilar"],
                        "总数量": category_info["total"],
                        "相似比例": category_info["ratio"],
                    }
                )
        else:
            pudu_rows = {}
            for sim_name, sim_info in dataset_info["categories"].items():
                for category_name, category_info in sim_info["categories"].items():
                    dic = pudu_rows.get(
                        category_name,
                        {
                            "数据集": dataset_name,
                            "类别": category_name,
                            "相似数量": 0,
                            "不相似数量": 0,
                            "总数量": 0,
                            "相似比例": 0.0,
                        },
                    )
                    dic["数据集"] = dataset_name
                    dic["类别"] = category_name
                    dic["相似数量"] += category_info["similar"]
                    dic["不相似数量"] += category_info["dissimilar"]
                    dic["总数量"] += category_info["total"]
                    dic["相似比例"] = (
                        dic["相似数量"] / dic["总数量"] if dic["总数量"] > 0 else 0
                    )
                    pudu_rows[category_name] = dic

            for value in pudu_rows.values():
                rows.append(value)

    # 转换为 DataFrame
    df = pd.DataFrame(rows)

    # 添加总的比例信息
    total_row = {
        "数据集": "总计",
        "类别": "",
        "相似数量": data["total_similar"],
        "不相似数量": data["total_dissimilar"],
        "总数量": data["total"],
        "相似比例": data["similar_ratio"],
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # 保存为 Excel 文件
    df.to_excel(output_file, index=False)
    print(f"数据已保存到 {output_file}")


if __name__ == "__main__":
    # JSON 文件路径
    json_file_path = r"d:\Project\uvProjects\ImageClassifier\logs\statistics.json"
    # 输出 Excel 文件路径
    output_excel_path = r"d:\Project\uvProjects\ImageClassifier\logs\statistics.xlsx"

    # 转换并保存
    json_to_excel(json_file_path, output_excel_path)
