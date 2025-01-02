from __future__ import absolute_import

import os
from raindrop.dropgenerator import generateDrops
from raindrop.config import cfg
from PIL import Image
import csv
from raindrop.raindrop import Raindrop

def load_drops_from_csv(csv_path):
    """
    Load raindrop data from a CSV file and create a list of Raindrop objects.

    :param csv_path: Path to the CSV file containing raindrop data.
    :return: List of Raindrop objects.
    """
    list_of_drops = []
    with open(csv_path, mode="r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            key, center_x, center_y, radius, shape = map(int, row[:5])
            list_of_drops.append(Raindrop(key, (center_x, center_y), radius, shape))
    return list_of_drops

def process_images(input_folder_path, output_folder_path, list_of_drops):
    """
    Process images in the specified folder by adding raindrop effects.

    :param input_folder_path: Path to the input image folder.
    :param output_folder_path: Path to save the processed images.
    :param list_of_drops: List of Raindrop objects.
    """
    for image_folder_name in os.listdir(input_folder_path):
        folder_path = os.path.join(input_folder_path, image_folder_name)
        if not os.path.isdir(folder_path):
            continue

        output_subfolder_path = os.path.join(output_folder_path, image_folder_name)
        os.makedirs(output_subfolder_path, exist_ok=True)

        for file_name in os.listdir(folder_path):
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            image_path = os.path.join(folder_path, file_name)
            output_image, _, _ = generateDrops(image_path, cfg, list_of_drops)
            save_path = os.path.join(output_subfolder_path, file_name)
            output_image.save(save_path)
            print(f"Saved {save_path}")

if __name__ == "__main__":
    # Paths and configurations
    csv_folder_path = "csv_data/"
    csv_paths = [
        os.path.join(csv_folder_path, f"drops{i}.csv") for i in range(1, 10)
    ]
    image_folders = {
        f"/home/yoshi-22/UniAD/data/nuscenes/samples{i}": f"/home/yoshi-22/UniAD/ROLE/nuscenes/samples" for i in range(1, 10)
    }
    image_folders.update({
        f"/home/yoshi-22/UniAD/data/nuscenes/sweeps{i}": f"/home/yoshi-22/UniAD/ROLE/nuscenes/sweeps" for i in range(1, 10)
    })

    print("image_folders:", image_folders)

    for output_folder_path in image_folders.keys():
        os.makedirs(output_folder_path, exist_ok=True)

    # Process images for each CSV and folder pair
    for i, csv_path in enumerate(csv_paths, start=1):
        list_of_drops = load_drops_from_csv(csv_path)
        for output_folder_path, input_folder_path in image_folders.items():
            if f"samples{i}" in output_folder_path or f"sweeps{i}" in output_folder_path:
                print(f"Processed images in {input_folder_path} and saved to {output_folder_path}")
                process_images(input_folder_path, output_folder_path, list_of_drops)
            else:
                print(f"Skipping {input_folder_path} as it does not contain samples{i} or sweeps{i}")


