import pandas as pd

# 入力ファイルのパス
input_file = "ego_steer.csv"

# CSVファイルを読み込み
data = pd.read_csv(input_file)

# ステアリング角度の列名（ファイルに応じて変更）
steering_column = "Steering Angle"

# 範囲ごとにデータをフィルタリング
data_neg_10_to_neg_1 = data[(data[steering_column] >= -10) & (data[steering_column] < -1)]
data_neg_1_to_pos_1 = data[(data[steering_column] >= -1) & (data[steering_column] <= 1)]
data_pos_1_to_pos_10 = data[(data[steering_column] > 1) & (data[steering_column] <= 10)]

# フィルタリングしたデータをそれぞれ新しいCSVに保存
data_neg_10_to_neg_1.to_csv("negative_10_to_negative_1.csv", index=False)
data_neg_1_to_pos_1.to_csv("negative_1_to_positive_1.csv", index=False)
data_pos_1_to_pos_10.to_csv("positive_1_to_positive_10.csv", index=False)

print("データを分割して保存しました。")
