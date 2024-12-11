import urllib.request
import time
import os

ts = time.time()
url = "http://review.xreco-retrieval.ch/api/assets/resource/efc25592-f560-484c-ab8e-683e92c211e5/asset.png"
filename = f'image_{url.split("/")[-1]}_{int(ts)}.jpg'
file_path = os.path.join(f'dataset/', filename)

# Create a request with a user-agent header
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

req = urllib.request.Request(url, headers=headers)

try:
    # Send the request and retrieve the response
    response = urllib.request.urlopen(req)
    image_bytes = response.read()

    # Save the image bytes to the file path
    with open(file_path, 'wb') as file:
        file.write(image_bytes)
    print(f"Image saved successfully as {file_path}")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} - {e.reason}")
except Exception as e:
    print(f"Error: {e}")

        