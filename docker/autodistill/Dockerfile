# Use official NVIDIA CUDA image - this tag EXISTS and is supported
FROM nvidia/cuda:12.9.1-devel-ubuntu20.04

# Prevent interactive prompts
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
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python dependencies in correct order
RUN pip3 install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.0.1 \
    numpy==1.24.3

# Install autodistill packages (latest working versions)
RUN pip3 install --no-cache-dir \
    autodistill==0.1.18 \
    autodistill-grounded-sam==0.1.5 \
    autodistill-yolov8==0.1.5

# Install additional dependencies
RUN pip3 install --no-cache-dir \
    sagemaker-training==4.6.0 \
    boto3==1.34.0 \
    pyyaml==6.0.1

# Set working directory
WORKDIR /opt/ml/processing

# Copy processing script
COPY process.py /opt/ml/processing/

# Set permissions
RUN chmod +x /opt/ml/processing/process.py

# Set entrypoint
ENTRYPOINT ["python3", "/opt/ml/processing/process.py"]

