import json
import csv
import os
import numpy as np

# CSVファイルとJSONファイルのパス
csv_file_paths = [
    "/home/yoshi-22/RaindropsOnWindshield/raindrops_generator/pose/negative_10_to_negative_1.csv",
    "/home/yoshi-22/RaindropsOnWindshield/raindrops_generator/pose/negative_1_to_positive_1.csv",
    "/home/yoshi-22/RaindropsOnWindshield/raindrops_generator/pose/positive_1_to_positive_10.csv",
]

json_file_paths = [
    "/home/yoshi-22/UniAD/test/base_e2e/bc_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/bl_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/br_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/mc_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/ml_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/mr_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/tc_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/bl_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/br_rain/results_nusc.json",
    "/home/yoshi-22/UniAD/test/base_e2e/no_rain/results_nusc.json",
]

# 出力ファイル
output_file_path = "/home/yoshi-22/RaindropsOnWindshield/raindrops_generator/results_summary_track.txt"

# 結果を出力ファイルに書き込み
with open(output_file_path, "w") as output_file:
    for csv_file_path in csv_file_paths:
        # CSVからtokenを取得
        with open(csv_file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            csv_tokens = {row["token"] for row in csv_reader}

        output_file.write(f"\nProcessing CSV file: {os.path.basename(csv_file_path)}\n")
        print(f"\nProcessing CSV file: {os.path.basename(csv_file_path)}")

        for json_file_path in json_file_paths:
            # JSONファイル名の前の部分（例: bc_rain）を取得
            json_name_part = os.path.basename(json_file_path).split('_')[0]

            # JSONファイルを読み込む
            with open(json_file_path, "r") as json_file:
                json_data = json.load(json_file)

            # 一致するtokenのデータをフィルタリング
            filtered_detections = []
            for token, detections in json_data["results"].items():
                if token in csv_tokens:
                    filtered_detections.extend(detections)

            # 全体のスコア平均を計算
            all_scores = [detection["tracking_score"] for detection in filtered_detections]
            overall_average = np.mean(all_scores) if all_scores else 0

            # detection_nameごとのスコア平均を計算
            detection_scores_by_name = {}
            for detection in filtered_detections:
                name = detection["tracking_name"]
                score = detection["tracking_score"]
                if name not in detection_scores_by_name:
                    detection_scores_by_name[name] = []
                detection_scores_by_name[name].append(score)

            # 各カテゴリの平均を計算
            category_averages = {
                name: np.mean(scores) for name, scores in detection_scores_by_name.items()
            }

            # 結果を表示およびファイルに書き込み
            output_file.write(f"JSON file: {json_file_path}\n")
            output_file.write(f" tracking Overall Score Average: {overall_average:.4f}\n")
            print(f"JSON file: {json_file_path}")
            print(f"  Overall Score Average: {overall_average:.4f}")

            for name, avg_score in category_averages.items():
                output_file.write(f"  {name}: {avg_score:.4f}\n")
                print(f"  {name}: {avg_score:.4f}")

print(f"Results written to {output_file_path}")
