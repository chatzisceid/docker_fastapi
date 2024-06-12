from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import base64
import subprocess
import json
import os
import aiofiles
from fastapi.responses import FileResponse
import requests
from typing import List
from connection_manager import ConnectionManager
from fastapi import BackgroundTasks
import urllib.request
import time

from scripts.create_tsv import create_image_data_tsv
from scripts.run_colmap import colmap_sparse_reconstruction, rename_folder

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Here you can receive messages and process them
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class ImageData(BaseModel):
    url: str

class MultiImageData(BaseModel):
    id: str
    images: List[ImageData]  

class Parameters(BaseModel):
    id: str
    epochs: int
    downscale: int

@app.post("/upload")
async def upload_images(data: MultiImageData,background_tasks: BackgroundTasks):
    try:
        # Create the directory if it doesn't exist
        os.makedirs(f'dataset/{data.id}/dense/images', exist_ok=True)
        os.makedirs(f'dataset/{data.id}/dense/0', exist_ok=True)

        # Define the data
        status = {
            "id": data.id,
            "progress ": f"{len(data.images)} images URL received",
            "status": "Images preprocess"
        }
        # Specify the filename
        status_f = f'{data.id}.json'
        # Write the data to the JSON file
        with open(status_f, 'w') as file:
            json.dump(status, file)

        background_tasks.add_task(process_image,data.images,data.id)
        return {"Images Received"}


    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/reconstruct")
async def upload_images(data: Parameters,background_tasks: BackgroundTasks):
    # Update the status dictionary
    status = {
        "id": data.id,
        "progress": f"0 of {data.epochs} epochs",
        "status": "training"
    }
    # Specify the filename
    status_f = f'{data.id}.json'       
    # Write the updated data to the JSON file
    with open(status_f, 'w') as file:
        json.dump(status, file)
    #execute train.py using subprocess
    train_script_path = 'train.py'

    train_args = [
        "--img_downscale", "256",
        "--root_dir", "dataset/1/",
        "--num_epochs", "10",
        "--id","xxx1"
    ]
    command = ['python3', train_script_path] + train_args
    # background_tasks.add_task(subprocess.run(command, check=True, shell=False))
    # return {"message": "Training started"}
    # Start the training process in the background
  #  subprocess.Popen(command)
    
    print("Training started.")
    return {"message": "Training started"}

@app.get("/download/{id}")
def get_mesh(id: str):
    filename = f"{id}.ply"
    return FileResponse(filename, media_type="model/ply")

@app.get("/status/{id}")
def get_status(id: str):
    filename = f"{id}.json"
    return FileResponse(filename, media_type="application/json")

def process_image(data_images,data_id):
    for image_data in data_images:

        # Update the progress message
        index = 0
        progress = f"{index} of {len(data_images)} images"
        index = index + 1
        # Update the status dictionary
        status = {
            "id": data_id,
            "progress": progress,
            "status": "Preprocessing Images"
        }
        # Specify the filename
        status_f = f'{data_id}.json'       
        # Write the updated data to the JSON file
        with open(status_f, 'w') as file:
            json.dump(status, file)

        # Generate a filename based on the ID and timestamp
        ts = time.time()
        #filename = f'image_{int(ts)}.jpg'
        filename = f'image_{image_data.url.split("/")[-1]}_{int(ts)}.jpg'
        file_path = os.path.join(f'dataset/{data_id}/dense/images', filename)
        # Convert base64 string to bytes
        #urllib.request.urlretrieve(image_data, file_path)
            # Download the image from the URL
        response = urllib.request.urlopen(image_data.url)
        image_bytes = response.read()
        
        # Save the image bytes to the file path
        with open(file_path, 'wb') as file:
            file.write(image_bytes)
            
        # Optionally, perform background tasks here
        # background_tasks.add_task(some_background_task, image_bytes)

    print("Images saved successfully!")

    # Create TSV file
    create_image_data_tsv(f'dataset/{data_id}/dense/images',f'dataset/{data_id}/image_data.tsv')
    print("TSV created..")

    # Provide the folder path containing the images
    image_folder_path = f'dataset/{data_id}/dense/images'

    # Provide the path where you want to save the sparse reconstruction
    output_sparse_path = f'dataset/{data_id}/dense'

    # Run COLMAP sparse reconstruction on the specified folder
    colmap_sparse_reconstruction(image_folder_path, output_sparse_path)
    rename_folder(f'dataset/{data_id}/dense/0', f'dataset/{data_id}/dense/sparse')
    print("Sparse reconstruction completed successfully!")
    # Update the status dictionary
    status = {
        "id": data_id,
        "progress": "Done",
        "status": "Ready for reconstruction"
    }
    # Specify the filename
    status_f = f'{data_id}.json'       
    # Write the updated data to the JSON file
    with open(status_f, 'w') as file:
        json.dump(status, file)
