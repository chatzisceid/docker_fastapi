import json
import base64
import time
import os

# Open the image file in binary mode, read it, and encode it to Base64
with open('test.jpg', 'rb') as file:
    image_data = file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

# Get the current timestamp
timestamp = time.time()

# Get the root directory
root_dir = os.path.dirname(os.path.abspath('image.jpg'))
id = 1

# Create a dictionary and include the Base64 image data, timestamp, and root directory
data = {
    'id': id,
    'timestamp': timestamp,
    'image': base64_image
}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

# Write the JSON data to a file
with open('output.json', 'w') as file:
    file.write(json_data)
