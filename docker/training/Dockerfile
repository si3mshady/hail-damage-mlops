FROM nvidia/cuda:11.8-devel-ubuntu20.04

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
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch first
RUN pip3 install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    torchaudio==2.0.2

# Install training dependencies
RUN pip3 install --no-cache-dir \
    ultralytics==8.0.196 \
    mlflow==2.7.1 \
    boto3==1.28.85 \
    sagemaker-training==4.5.4 \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.0.1 \
    pyyaml==6.0.1 \
    matplotlib==3.7.2 \
    seaborn==0.12.2

# Set working directory
WORKDIR /opt/ml/code

# Copy training script
COPY train.py /opt/ml/code/

# Set permissions
RUN chmod +x /opt/ml/code/train.py

# Set entrypoint
ENTRYPOINT ["python3", "/opt/ml/code/train.py"]

