from nuscenes.can_bus.can_bus_api import NuScenesCanBus
import matplotlib.pyplot as plt
import csv

# nuScenes CAN busデータのロード
nusc_can = NuScenesCanBus(dataroot='/home/yoshi-22/UniAD/data/nuscenes/can_bus')

# プロットするシーンとメッセージを指定
scene_name = 'scene-0001'
message_name = 'steeranglefeedback'
key_name = 'value'

# データを取得
data = nusc_can.get_messages(scene_name, message_name)

# タイムスタンプと値を抽出
timestamps = [entry['utime'] for entry in data]  # マイクロ秒単位のタイムスタンプ
values = [entry[key_name] for entry in data]     # ステアリング角度の値

# タイムスタンプを秒単位に変換（オプション）
timestamps = [(t - timestamps[0]) / 1e6 for t in timestamps]  # 最初のタイムスタンプを基準に秒単位に変換

# CSVに保存
output_file = 'steering_angle_data.csv'
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time (s)', 'Steering Angle (radians)'])
    for time, value in zip(timestamps, values):
        writer.writerow([time, value])

print(f"Data saved to {output_file}")

# プロット
plt.figure(figsize=(10, 6))
plt.plot(timestamps, values, label='Steering Angle', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Steering Angle (radians)')
plt.title(f'Steering Angle over Time ({scene_name})')
plt.legend()
plt.grid(True)
plt.show()
