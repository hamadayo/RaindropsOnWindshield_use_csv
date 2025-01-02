from __future__ import absolute_import

import os
from raindrop.dropgenerator import generateDrops, generate_label
from raindrop.config import cfg
from PIL import Image
import numpy as np
from raindrop.raindrop import Raindrop
import csv

width = 1600
height = 900

image_folder_path = "input/"
outputimg_folder_path = "output/"
mask_folder_path = "masks/"
csv_folder_path = "csv_data_forth/"

a_main = os.listdir(image_folder_path)
if '.DS_Store' in a_main:
    a_main.remove('.DS_Store')
    
for folder_name in a_main:
    
    in_folder = image_folder_path + folder_name

    out_folder = outputimg_folder_path + folder_name
#   os.mkdir(out_folder)
    mask_folder = mask_folder_path + folder_name
#   os.mkdir(mask_folder)
    csv_path = os.path.join(csv_folder_path, f"{folder_name}_drops.csv")
    os.makedirs(csv_folder_path, exist_ok=True)

    List_of_Drops, _  = generate_label(height, width, cfg)

     # 雨滴リストをCSVに書き込む
    with open(csv_path, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # CSVヘッダーを追加
        csv_writer.writerow(["Key", "CenterX", "CenterY", "Radius", "Shape"])
        for drop in List_of_Drops:
            key = drop.getKey()
            center_x, center_y = drop.getCenters()
            radius = drop.getRadius()
            shape = drop.shape
            csv_writer.writerow([key, center_x, center_y, radius, shape])

    a = os.listdir(in_folder)
    if '.DS_Store' in a:
        a.remove('.DS_Store')

    for file_name in a:
        image_path = os.path.join(in_folder, file_name)
        output_image, output_label, mask = generateDrops(image_path, cfg, List_of_Drops)

        save_path = os.path.join(out_folder, file_name)
        mask_path = os.path.join(mask_folder, file_name)

        output_image.save(save_path)
        mask.save(mask_path)
