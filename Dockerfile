ARG CUDA_VERSION=11.8.0
ARG OS_VERSION=22.04
ARG USER_ID=1000
# Define base image.
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${OS_VERSION}
ARG CUDA_VERSION
ARG OS_VERSION
ARG USER_ID

# metainformation
LABEL org.opencontainers.image.version="0.1.18"
LABEL org.opencontainers.image.source="https://github.com/nerfstudio-project/nerfstudio"
LABEL org.opencontainers.image.licenses="Apache License 2.0"
LABEL org.opencontainers.image.base.name="docker.io/library/nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${OS_VERSION}"

# Variables used at build time.
## CUDA architectures, required by Colmap and tiny-cuda-nn.
## NOTE: All commonly used GPU architectures are included and supported here. To speedup the image build process remove all architectures but the one of your explicit GPU. Find details here: https://developer.nvidia.com/cuda-gpus (8.6 translates to 86 in the line below) or in the docs.
ARG CUDA_ARCHITECTURES=90;89;86;80;75;70;61;52;37

# Set environment variables.
## Set non-interactive to prevent asking for user inputs blocking image creation.
ENV DEBIAN_FRONTEND=noninteractive
## Set timezone as it is required by some packages.
ENV TZ=Europe/Berlin
## CUDA Home, required to find CUDA in some packages.
ENV CUDA_HOME="/usr/local/cuda"

# Install required apt packages and clear cache afterwards.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    ffmpeg \
    git \
    libatlas-base-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-test-dev \
    libhdf5-dev \
    libcgal-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libgflags-dev \
    libglew-dev \
    libgoogle-glog-dev \
    libmetis-dev \
    libprotobuf-dev \
    libqt5opengl5-dev \
    libsqlite3-dev \
    libsuitesparse-dev \
    nano \
    protobuf-compiler \
    python-is-python3 \
    python3.10-dev \
    python3-pip \
    qtbase5-dev \
    sudo \
    vim-tiny \
    wget && \
    rm -rf /var/lib/apt/lists/*

    # Install GLOG (required by ceres).
RUN git clone --branch v0.6.0 https://github.com/google/glog.git --single-branch && \
cd glog && \
mkdir build && \
cd build && \
cmake .. && \
make -j `nproc` && \
make install && \
cd ../.. && \
rm -rf glog
# Add glog path to LD_LIBRARY_PATH.
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

# Install Ceres-solver (required by colmap).
RUN git clone --branch 2.1.0 https://ceres-solver.googlesource.com/ceres-solver.git --single-branch && \
cd ceres-solver && \
git checkout $(git describe --tags) && \
mkdir build && \
cd build && \
cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
make -j `nproc` && \
make install && \
cd ../.. && \
rm -rf ceres-solver

# Install colmap.
RUN git clone --branch 3.8 https://github.com/colmap/colmap.git --single-branch && \
cd colmap && \
mkdir build && \
cd build && \
cmake .. -DCUDA_ENABLED=ON \
         -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} && \
make -j `nproc` && \
make install && \
cd ../.. && \
rm -rf colmap

# Create non root user and setup environment.
RUN useradd -m -d /home/user -g root -G sudo -u ${USER_ID} user
RUN usermod -aG sudo user
# Set user password
RUN echo "user:user" | chpasswd
# Ensure sudo group users are not asked for a password when using sudo command by ammending sudoers file
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Switch to new uer and workdir.
USER ${USER_ID}
WORKDIR /home/user

# Add local user binary folder to PATH variable.
ENV PATH="${PATH}:/home/user/.local/bin"
SHELL ["/bin/bash", "-c"]

# Upgrade pip and install packages.
RUN python3.10 -m pip install --no-cache-dir --upgrade pip setuptools pathtools promise pybind11
# Install pytorch and submodules
RUN CUDA_VER=${CUDA_VERSION%.*} && CUDA_VER=${CUDA_VER//./} && python3.10 -m pip install --no-cache-dir \
    torch==2.0.1+cu${CUDA_VER} \
    torchvision==0.15.2+cu${CUDA_VER} \
        --extra-index-url https://download.pytorch.org/whl/cu${CUDA_VER}
# Install tynyCUDNN (we need to set the target architectures as environment variable first).
ENV TCNN_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES}
RUN python3.10 -m pip install --no-cache-dir git+https://github.com/NVlabs/tiny-cuda-nn.git@v1.6#subdirectory=bindings/torch

# Copy the requirements file into the container
COPY requirements.txt .
# COPY torch-1.13.1+cu117-cp310-cp310-linux_x86_64.whl .
# COPY torchvision-0.14.1+cu117-cp310-cp310-linux_x86_64.whl .
# COPY torchaudio-0.13.1+cu117-cp310-cp310-linux_x86_64.whl .

# Install the .whl files
# RUN pip uninstall -y torch
# RUN pip install --no-cache-dir torch-1.13.1+cu117-cp310-cp310-linux_x86_64.whl
# RUN pip install --no-cache-dir torchvision-0.14.1+cu117-cp310-cp310-linux_x86_64.whl
# RUN pip install --no-cache-dir torchaudio-0.13.1+cu117-cp310-cp310-linux_x86_64.whl

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#install pytorch scatter
RUN pip install torch-scatter -f https://data.pyg.org/whl/torch-2.0.0+cu118.html

#numpy older version
RUN python3.10 -m pip uninstall -y numpy
RUN python3.10 -m pip install numpy==1.26.4

# Copy the FastAPI application into the container
WORKDIR /app
COPY app/ .

# Install Apex
RUN git clone https://github.com/NVIDIA/apex
WORKDIR /app/apex
RUN pip install -v --disable-pip-version-check --no-build-isolation --no-cache-dir .

#Install vren
COPY models/ /app/models/
#RUN pip install /app/models/csrc

WORKDIR /app

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI server within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]