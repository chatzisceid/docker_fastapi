import subprocess

def colmap_sparse_reconstruction(image_path, output_path):
    try:
        # Feature extraction
        subprocess.run(['colmap', 'feature_extractor', '--database_path', 'db.db', '--image_path', image_path, '--SiftExtraction.use_gpu', '0'], check=True)

        # Feature matching
        subprocess.run(['colmap', 'exhaustive_matcher', '--database_path', 'db.db'], check=True)

        # Sparse reconstruction
        subprocess.run(['colmap', 'mapper', '--database_path', 'db.db', '--image_path', image_path, '--output_path', output_path], check=True)
        
        print("Sparse reconstruction completed successfully!")

    except subprocess.CalledProcessError as e:
        print("Sparse reconstruction failed:", e)

# Provide the folder path containing the images
image_folder_path = 'new/dataset/dense/images'

# Provide the path where you want to save the sparse reconstruction
output_sparse_path = 'new/dataset/dense'

# Run COLMAP sparse reconstruction on the specified folder
colmap_sparse_reconstruction(image_folder_path, output_sparse_path)