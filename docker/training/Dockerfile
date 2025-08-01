# Use official NVIDIA CUDA image - this tag EXISTS and is supported
FROM nvidia/cuda:12.9.1-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch with CUDA support (matching CUDA 12.9)
RUN pip3 install --no-cache-dir \
    torch==2.1.0+cu121 \
    torchvision==0.16.0+cu121 \
    torchaudio==2.1.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Install training dependencies
RUN pip3 install --no-cache-dir \
    ultralytics==8.0.230 \
    mlflow==2.8.1 \
    boto3==1.34.0 \
    sagemaker-training==4.6.0 \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.0.1 \
    pyyaml==6.0.1 \
    matplotlib==3.8.2 \
    seaborn==0.13.0

# Set working directory
WORKDIR /opt/ml/code

# Copy training script
COPY train.py /opt/ml/code/

# Set permissions
RUN chmod +x /opt/ml/code/train.py

# Set entrypoint
ENTRYPOINT ["python3", "/opt/ml/code/train.py"]

