from fastapi import FastAPI
from pydantic import BaseModel
import base64
import json
import os
import aiofiles
from fastapi.responses import FileResponse

app = FastAPI()

class ImageData(BaseModel):
    id : int
    timestamp: float
    image: str

@app.post("/upload")
async def upload_file(data: ImageData):
    try:
        # Decode the Base64 image data
        image_data = base64.b64decode(data.image)

        # Print the current working directory and the first 100 characters of the image data
        print("Current working directory:", os.getcwd())
        print("Image data (first 100 characters):", data.image[:100])

        # Save the image data to a file asynchronously
        async with aiofiles.open('output.jpg', 'wb') as file:
            await file.write(image_data)

        return {"status": "Image received and saved"}

        # # Save the image data to a file
        # with open('output.jpg', 'wb') as file:
        #     file.write(image_data)

        # return {"status": "Image received and saved"}

    except Exception as e:
        # If there's an error, return a response with the error message
        return {"status": "Error", "message": str(e)}
    
# @app.get("/download")
# async def download_file():
#     file_path = '/app/output.jpg'  # Update the path according to where the file is saved
#     return FileResponse(file_path)
@app.get("/download")
async def download_file():
    file_path = '/app/output.jpg'  # Update the path according to where the file is saved
    return FileResponse(file_path, media_type='image/jpeg', filename='client_output.jpg')