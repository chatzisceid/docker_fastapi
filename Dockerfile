# # Use Ubuntu 20.04 as the base image
# FROM python:3.10

# Use a base image that supports CUDA
# FROM nvidia/cuda:12.0.0-base-ubuntu20.04
FROM ubuntu:22.04

# Set environment variables for CUDA compatibility
ENV DEBIAN_FRONTEND=noninteractive
ENV NV_ARCH=x86_64
ENV NVIDIA_REQUIRE_CUDA="cuda>=11.7 brand=tesla,driver>=470,driver<471"

# Update package lists and install necessary packages
# RUN apt-get update && \
#     apt-get install -y \
#     cuda \
#     && rm -rf /var/lib/apt/lists/*
# RUN apt-get update
# RUN apt-get install -y wget
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
# RUN mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
# RUN wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-ubuntu2204-11-7-local_11.7.0-515.43.04-1_amd64.deb
# RUN dpkg -i cuda-repo-ubuntu2204-11-7-local_11.7.0-515.43.04-1_amd64.deb
# RUN cp /var/cuda-repo-ubuntu2204-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
# RUN apt-get update
# RUN apt-get -y install cuda

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/${NV_ARCH}/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/${NV_ARCH} /" > /etc/apt/sources.list.d/cuda.list && \
    apt-get purge --autoremove -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-toolkit-11-7 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables (optional but recommended)
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY torch-1.13.1+cu117-cp310-cp310-linux_x86_64.whl .
COPY torchvision-0.14.1+cu117-cp310-cp310-linux_x86_64.whl .
COPY torchaudio-0.13.1+cu117-cp310-cp310-linux_x86_64.whl .
COPY vren-2.0-cp310-cp310-linux_x86_64.whl .

COPY models/ /app/models/

# Update package lists
RUN apt-get update

# Install necessary packages to add a new repository
RUN apt-get install -y software-properties-common

# Add the Deadsnakes PPA (Personal Package Archive) to your system
# The Deadsnakes PPA contains more recent Python versions than the default Ubuntu repositories
RUN add-apt-repository ppa:deadsnakes/ppa

# Update package lists again after adding the new repository
RUN apt-get update

# Install Python 3.10
RUN apt-get install -y python3.10
RUN apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip
RUN apt install git -y

# Install the .whl files
RUN pip install --no-cache-dir torch-1.13.1+cu117-cp310-cp310-linux_x86_64.whl
RUN pip install --no-cache-dir torchvision-0.14.1+cu117-cp310-cp310-linux_x86_64.whl
RUN pip install --no-cache-dir torchaudio-0.13.1+cu117-cp310-cp310-linux_x86_64.whl
RUN pip install --no-cache-dir vren-2.0-cp310-cp310-linux_x86_64.whl

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Install python-multipart
RUN pip install python-multipart

# Set environment variables
ENV COLMAP_VERSION="3.6"

# Build and install COLMAP

# Note: This Dockerfile has been tested using COLMAP pre-release 3.7.
# Later versions of COLMAP (which will be automatically cloned as default) may
# have problems using the environment described thus far. If you encounter
# problems and want to install the tested release, then uncomment the branch
# specification in the line below
RUN git clone https://github.com/colmap/colmap.git

# RUN cd colmap && \
# 	git checkout dev && \
# 	mkdir build && \
# 	cd build && \
# 	cmake .. && \
# 	make -j4 && \
# 	make install

# Install COLMAP
# RUN apt-get update && apt-get install -y colmap

#Install vren
# RUN pip install /app/models/csrc

# Copy the FastAPI application into the container
COPY app/ .

# Copy the image directory from the local machine to the container
# COPY brandenburg_gate/ /app/brandenburg_gate/

RUN apt-get update && apt-get install -y libqt5gui5
RUN apt-get update && apt-get install -y xvfb
ENV QT_DEBUG_PLUGINS=1
ENV QT_QPA_PLATFORM=minimal
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

RUN rm -rf /var/lib/apt/lists/*

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI server within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
