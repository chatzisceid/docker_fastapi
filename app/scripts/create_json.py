import json
import base64
import time
import os

def create_image_json(folder_path):
    images_list = []
    id = 1

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.png', '.jpeg')):  # Filter only image files
            image_path = os.path.join(folder_path, filename)

            with open(image_path, 'rb') as file:
                image_data = file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

                timestamp = time.time()

                image_dict = {
                    'id': id,
                    'timestamp': timestamp,
                    'image_base64': base64_image
                }

                images_list.append(image_dict)
                id += 1

    json_data = {'images': images_list}

    with open('output.json', 'w') as file:
        json.dump(json_data, file, indent=2)

# Provide the path to the folder containing images
folder_path = '/media/chatzise/E0E43345E4331CEA/dataset_test/'
create_image_json(folder_path)