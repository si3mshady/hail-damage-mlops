FROM nvidia/cuda:12.9.1-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    imagemagick \
    wget \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch first - stable version
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    numpy==1.24.3

# Install autodistill - use LATEST stable versions (don't pin unnecessarily)
RUN pip3 install --no-cache-dir \
    autodistill \
    autodistill-grounded-sam \
    autodistill-yolov8

# Install supporting packages
RUN pip3 install --no-cache-dir \
    opencv-python-headless \
    Pillow \
    sagemaker-training \
    boto3 \
    pyyaml

# Set working directory
WORKDIR /opt/ml/processing

# Copy processing script
COPY process.py /opt/ml/processing/

# Set permissions
RUN chmod +x /opt/ml/processing/process.py

# Set entrypoint
ENTRYPOINT ["python3", "/opt/ml/processing/process.py"]

