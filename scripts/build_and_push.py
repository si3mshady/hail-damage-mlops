#!/usr/bin/env python3
import subprocess
import sys
import boto3
import base64

# Your Terraform outputs
ECR_TRAINING_REPO = "564230509626.dkr.ecr.us-east-2.amazonaws.com/hail-damage-57htv0-training"
ECR_INFERENCE_REPO = "564230509626.dkr.ecr.us-east-2.amazonaws.com/hail-damage-57htv0-inference"
AWS_REGION = "us-east-2"
AWS_ACCOUNT_ID = "564230509626"

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"🔧 {description}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:  
            print(f"STDERR: {e.stderr}")
        return False

def login_to_ecr():
    """Login to ECR"""
    print("🔐 Logging into ECR...")
    
    # Get ECR login token
    ecr_client = boto3.client('ecr', region_name=AWS_REGION)
    try:
        token = ecr_client.get_authorization_token()
        username, password = base64.b64decode(
            token['authorizationData'][0]['authorizationToken']
        ).decode().split(':')
        
        # Docker login
        return run_command([
            'docker', 'login', '--username', username, '--password-stdin',
            f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
        ], "ECR Docker login")
        
    except Exception as e:
        print(f"❌ ECR login failed: {e}")
        return False

def build_and_push_container(dockerfile_path, repo_url, container_name):
    """Build and push a single container"""
    print(f"\n🏗️ Building {container_name} container...")
    
    # Build
    if not run_command([
        'docker', 'build', '-t', f"{repo_url}:latest", dockerfile_path
    ], f"Building {container_name}"):
        return False
    
    # Push
    if not run_command([
        'docker', 'push', f"{repo_url}:latest"
    ], f"Pushing {container_name}"):
        return False
    
    print(f"✅ {container_name} container built and pushed successfully!")
    return True

def main():
    print("🚀 Starting Docker build and push process...")
    
    # Login to ECR
    if not login_to_ecr():
        print("❌ ECR login failed")
        sys.exit(1)
    
    # Build and push autodistill container
    if not build_and_push_container(
        "docker/autodistill/", 
        ECR_TRAINING_REPO,  # Using training repo for processing
        "Autodistill Processing"
    ):
        print("❌ Autodistill container build failed")
        sys.exit(1)
    
    # Build and push training container  
    if not build_and_push_container(
        "docker/training/",
        ECR_INFERENCE_REPO,  # Using inference repo for training
        "YOLOv8 Training"
    ):
        print("❌ Training container build failed")
        sys.exit(1)
    
    print("\n🎉 All containers built and pushed successfully!")
    print(f"📦 Autodistill: {ECR_TRAINING_REPO}:latest")
    print(f"📦 Training: {ECR_INFERENCE_REPO}:latest")

if __name__ == "__main__":
    main()

