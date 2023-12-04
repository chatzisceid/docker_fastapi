import os

def create_image_data_tsv(folder_path, tsv_file_path):
    # Get all filenames in the folder
    filenames = os.listdir(folder_path)

    # Sort filenames to maintain order
    filenames.sort()

    # Create and write to the TSV file
    with open(tsv_file_path, 'w') as tsvfile:
        # Write the header
        tsvfile.write("filename\tid\tsplit\tdataset\n")

        # Write data for each filename
        for idx, filename in enumerate(filenames, start=1):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.jpg'):  # Check if it's a JPG file
                image_id = float(idx)  # Convert image_id to float64
                split = 'train'
                dataset = 'custom'

                # Writing in the specified format
                tsvfile.write(f"{filename}\t{image_id}\t{split}\t{dataset}\n")