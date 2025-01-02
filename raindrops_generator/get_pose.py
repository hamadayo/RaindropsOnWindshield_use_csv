from nuscenes.nuscenes import NuScenes
import numpy as np
import csv

# nuScenesデータセットのパス
nusc = NuScenes(version='v1.0-mini', dataroot='/home/yoshi-22/UniAD/data/nuscenes', verbose=True)

# 例として、CAM_FRONTのデータを取得
sensor_channel = 'CAM_FRONT'
scene_token = nusc.scene[0]['token']  # 例として最初のシーンを選択
print(f"Scene token: {scene_token}")

# シーンの最初のsampleデータを取得
sample_token = nusc.get('scene', scene_token)['first_sample_token']
# 実際に処理した画像の数をカウント
processed_images = []
output_file = 'ego_pose.csv'

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Scene Name', 'Image Filename', 'Position X', 'Position Y', 'Position Z', 'Rotation W', 'Rotation X', 'Rotation Y', 'Rotation Z', 'Steering Angle'])

    for scene in nusc.scene:
        print(scene['name'])
        sample_token = scene['first_sample_token']
        # カメラ画像に対応するego_poseを取得
        while sample_token:
            sample = nusc.get('sample', sample_token)
            cam_data = nusc.get('sample_data', sample['data'][sensor_channel])
            ego_pose = nusc.get('ego_pose', cam_data['ego_pose_token'])
            # ここにステアリング角度を取得する処理を追加
            stter_angle = None
            can_data_token = sample['data'].get('CAN_BUS', None)
            if can_data_token:
                can_data = nusc.get('sample_data', can_data_token)
                can = nusc.get('can_bus', can_data['can_bus'])
                steering_angle = can['steering_angle']
            else:
                steering_angle = None
            
            # ファイル名を保存
            writer.writerow([scene['name'], cam_data['filename'], ego_pose['translation'][0], ego_pose['translation'][1], ego_pose['translation'][2], ego_pose['rotation'][0], ego_pose['rotation'][1], ego_pose['rotation'][2], ego_pose['rotation'][3]])
                            
            processed_images.append(cam_data['filename'])

            # # 画像ファイル名と姿勢データを出力
            # print(f"Image: {cam_data['filename']}")
            # print(f"Position: {ego_pose['translation']}")  # [x, y, z]
            # print(f"Rotation: {ego_pose['rotation']}")    # Quaternion [w, x, y, z]
            
            # 次のデータへ移動
            sample_token = sample['next']

print(f"Processed {len(processed_images)} images.")
