# Use Ubuntu 20.04 with Python 3.8 (matches your base system)
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

# Upgrade pip first
RUN python3 -m pip install --upgrade pip

# Install core dependencies with COMPATIBLE versions for Python 3.8
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    numpy==1.24.3

# Install ultralytics and related packages - use LATEST stable
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    Pillow

# Install AWS and MLflow packages - use COMPATIBLE versions
RUN pip3 install --no-cache-dir \
    mlflow==2.7.1 \
    boto3 \
    sagemaker-training \
    pyyaml

# Install matplotlib version that EXISTS for Python 3.8
RUN pip3 install --no-cache-dir \
    "matplotlib>=3.3.0,<3.8.0" \
    seaborn

# Set working directory
WORKDIR /opt/ml/code

# Copy training script
COPY train.py /opt/ml/code/

# Set permissions
RUN chmod +x /opt/ml/code/train.py

# Set entrypoint
ENTRYPOINT ["python3", "/opt/ml/code/train.py"]

