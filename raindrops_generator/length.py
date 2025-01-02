# 指定したフォルダのファイル数を調べるコードを書いて

import os

def count_files(folder_path):
    """
    Count the number of files in the specified folder.

    :param folder_path: Path to the folder.
    :return: Number of files in the folder.
    """
    # List all files in the folder
    files = os.listdir(folder_path)
    # Count the number of files
    num_files = len(files)
    return num_files

folder_path = "/home/yoshi-22/UniAD/data/nuscenes/samples/" 