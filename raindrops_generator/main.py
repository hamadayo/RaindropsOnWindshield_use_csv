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
originalDrop = Raindrop(1, (50, 50), 100, shape=0)
originalDrop2 = Raindrop(2, (800, 450), 150, shape=2)

a_main = os.listdir(image_folder_path)
if '.DS_Store' in a_main:
    a_main.remove('.DS_Store')
    
for folder_name in a_main:
    
    in_folder = image_folder_path + folder_name

    out_folder = outputimg_folder_path + folder_name
#   os.mkdir(out_folder)
    mask_folder = mask_folder_path + folder_name
#   os.mkdir(mask_folder)

    a = os.listdir(in_folder)
    if '.DS_Store' in a:
        a.remove('.DS_Store')

    for file_name in a:
        image_path = os.path.join(in_folder, file_name)

        output_image, output_label, mask = generateDrops(image_path, cfg, [originalDrop, originalDrop2])

        save_path = os.path.join(out_folder, file_name)
        mask_path = os.path.join(mask_folder, file_name)

        output_image.save(save_path)
        mask.save(mask_path)
