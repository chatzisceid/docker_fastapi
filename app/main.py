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
    id: int
    timestamp: float
    image_base64: str  # Change 'image' field to 'image_url'

class MultiImageData(BaseModel):
    images: List[ImageData]  

@app.post("/upload")
async def upload_images(data: MultiImageData,background_tasks: BackgroundTasks):
    try:
        # Create the directory if it doesn't exist
        os.makedirs('dataset/dense/images', exist_ok=True)
        os.makedirs('dataset/dense/0', exist_ok=True)

        for image_data in data.images:
            # Convert base64 string to bytes
            image_bytes = base64.b64decode(image_data.image_base64)

            # Generate a filename based on the ID and timestamp
            filename = f'image_{image_data.id}_{int(image_data.timestamp)}.jpg'
            file_path = os.path.join('dataset/dense/images', filename)

            # Save the image data to a file
            with open(file_path, 'wb') as file:
                file.write(image_bytes)

        print("Images saved successfully!")

        # Create TSV file
        create_image_data_tsv('dataset/dense/images','dataset/image_data.tsv')
        print("TSV created..")

        # Provide the folder path containing the images
        image_folder_path = 'dataset/dense/images'

        # Provide the path where you want to save the sparse reconstruction
        output_sparse_path = 'dataset/dense'

        # Run COLMAP sparse reconstruction on the specified folder
        colmap_sparse_reconstruction(image_folder_path, output_sparse_path)
        rename_folder('dataset/dense/0', 'dataset/dense/sparse')
        print("Sparse reconstruction completed successfully!")

        #execute train.py using subprocess
        train_script_path = 'train.py'
        # train_args = [
        #     "--img_downscale", "256",
        #     "--root_dir", "brandenburg_gate/",
        #     "--exp_name", "custom",
        #     "--dataset_name", "phototourism",
        #     "--num_epochs", "2",
        #     "--batch_size", "2048",
        #     "--lr", "5e-4",
        #     "--encode_a", "--encode_t",
        #     "--N_importance", "128",
        #     "--N_vocab", "1500"
        # ]
        train_args = [
            "--img_downscale", "256",
            "--root_dir", "dataset/",
            "--num_epochs", "2"
        ]
        command = ['python3', train_script_path] + train_args
        # background_tasks.add_task(subprocess.run(command, check=True, shell=False))
        # return {"message": "Training started"}
        try:
            subprocess.run(command, check=True, shell=False)
            print("train.py execution completed successfully!")
        except subprocess.CalledProcessError as e:
            print("train.py execution failed:", e)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/download")
async def download_file():
    file_path = 'data.json'  # Update the path according to where the file is saved

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Read the JSON file content
        with open(file_path, 'r') as file:
            data = file.read()

        print("Read data:", data)  # Print the read data for debugging

        if not data.strip():  # Check if the read data is empty or whitespace
            raise HTTPException(status_code=400, detail="File is empty")

        json_data = json.loads(data)  # Convert the read string to JSON

        print("Parsed JSON:", json_data)  # Print the parsed JSON data for debugging

        return {"data": json_data}  # Return the JSON data as a dictionary

    except json.JSONDecodeError as json_error:
        raise HTTPException(status_code=400, detail=str(json_error))  # Handle JSON decoding error

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))