from nuscenes.nuscenes import NuScenes
from nuscenes.can_bus.can_bus_api import NuScenesCanBus
import numpy as np
import csv

# nuScenesデータセットのパス
nusc = NuScenes(version='v1.0-mini', dataroot='/home/yoshi-22/UniAD/data/nuscenes', verbose=True)
nusc_can = NuScenesCanBus(dataroot='/home/yoshi-22/UniAD/data/nuscenes/can_bus')

# 例として、CAM_FRONTのデータを取得
sensor_channel = 'CAM_FRONT'
scene_token = nusc.scene[0]['token']  # 例として最初のシーンを選択
print(f"Scene token: {scene_token}")

# シーンの最初のsampleデータを取得
sample_token = nusc.get('scene', scene_token)['first_sample_token']
# 実際に処理した画像の数をカウント
processed_images = []
output_file = 'ego_steer.csv'

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['token', 'Scene Name', 'Image Filename', 'Steering Angle'])

    for scene in nusc.scene:
        print(scene['name'])
        sample_token = scene['first_sample_token']
        # ステアリング角度データを取得
        can_data = nusc_can.get_messages(scene['name'], 'steeranglefeedback')

        # カメラ画像に対応するego_poseを取得
        first_sample = True
        while sample_token:
            sample = nusc.get('sample', sample_token)
            print(f'sample {type(sample)}')
            print(f'sample{sample.keys()}')
            print(f'token {sample["token"]}')
            cam_data = nusc.get('sample_data', sample['data'][sensor_channel])
            ego_pose = nusc.get('ego_pose', cam_data['ego_pose_token'])

            # ego_poseのタイムスタンプ
            ego_timestamp = ego_pose['timestamp']

            # ステアリング角度をタイムスタンプに基づいて検索
            steering_angle = None
            search_range = 5e4 if first_sample else 1e4  # 最初のサンプルの場合は5秒以内、それ以外は1秒以内
            for entry in can_data:
                if abs(entry['utime'] - ego_timestamp) < search_range:  # 10ミリ秒以内のデータをマッチング
                    steering_angle = entry['value']
                    break
            
            first_sample = False

            # CSVに書き込み
            writer.writerow([
                sample['token'],
                scene['name'],
                cam_data['filename'],
                steering_angle
            ])

            processed_images.append(cam_data['filename'])

            # 次のデータへ移動
            sample_token = sample['next']
        nusc_can.plot_message_data(scene['name'], 'steeranglefeedback', 'value')

print(f"Processed {len(processed_images)} images and saved to {output_file}.")
