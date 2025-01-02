import os
import requests

def download_files(txt_file_path, save_directory):
    """
    Download files from URLs listed in a text file and save them to the specified directory.

    :param txt_file_path: Path to the text file containing URLs.
    :param save_directory: Directory to save the downloaded files.
    """
    # Create the save directory if it does not exist
    os.makedirs(save_directory, exist_ok=True)

    # Read the text file line by line
    with open(txt_file_path, 'r') as file:
        urls = file.readlines()

    # Loop through each URL and download the file
    for url in urls:
        url = url.strip()  # Remove any leading/trailing whitespace
        if not url:
            continue  # Skip empty lines

        try:
            # Get the file name from the URL
            file_name = os.path.basename(url)
            save_path = os.path.join(save_directory, file_name)

            print(f"Downloading {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Save the file to the specified directory
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            print(f"Saved: {save_path}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    # Path to the text file containing the URLs
    txt_file_path = "nuscenes_trainval.txt"  # Replace with the path to your text file

    # Directory where files will be saved
    save_directory = "/media/yoshi-22/iASL-data001/data/nuscenes"  # Replace with your desired directory

    # Download the files
    download_files(txt_file_path, save_directory)
