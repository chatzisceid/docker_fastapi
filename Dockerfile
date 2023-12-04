# Use the official Python image from Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install python-multipart
RUN pip install python-multipart

# Install COLMAP
RUN apt-get update && apt-get install -y colmap

# Copy the FastAPI application into the container
COPY app/ .

# Copy the image directory from the local machine to the container
COPY brandenburg_gate/ /app/brandenburg_gate/

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI server within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
