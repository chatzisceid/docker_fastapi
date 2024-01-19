import subprocess
import time
import os

def colmap_sparse_reconstruction(image_path, output_path):
    try:
        # Generate a timestamp for a unique database file
        timestamp = int(time.time())
        database_path = f'db_{timestamp}.db'

        # Create the output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Feature extraction
        subprocess.run(['colmap', 'feature_extractor', '--database_path', database_path, '--image_path', image_path, '--SiftExtraction.use_gpu', '0'], check=True)

        # Feature matching
        subprocess.run(['colmap', 'exhaustive_matcher', '--database_path', database_path, '--SiftMatching.use_gpu', '0'], check=True)

        # Sparse reconstruction
        subprocess.run(['colmap', 'mapper', '--database_path', database_path, '--image_path', image_path, '--output_path', output_path], check=True)
        
        print("Sparse reconstruction completed successfully!")

    except subprocess.CalledProcessError as e:
        print("Sparse reconstruction failed:", e)

def rename_folder(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print(f"Folder '{old_name}' renamed to '{new_name}' successfully!")
    except FileNotFoundError:
        print(f"Folder '{old_name}' does not exist!")
    except FileExistsError:
        print(f"Folder '{new_name}' already exists!")


# # Provide the folder path containing the images
# image_folder_path = '/media/chatzise/E0E43345E4331CEA/dataset_test/'

# # Provide the path where you want to save the sparse reconstruction
# output_sparse_path = 'dataset/dense'

# # Run COLMAP sparse reconstruction on the specified folder
# colmap_sparse_reconstruction(image_folder_path, output_sparse_path)
# rename_folder('dataset/dense/0', 'dataset/dense/sparse')
# print("Sparse reconstruction completed successfully!")