#!/usr/bin/env python3
import argparse
import boto3
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--model-prefix', required=True)
    args = parser.parse_args()
    
    print("🏗️ Setting up model deployment...")
    
    # Create SageMaker client
    sm = boto3.client('sagemaker', region_name='us-east-2')
    
    # Generate unique names
    timestamp = int(time.time())
    model_name = f"hail-damage-model-{timestamp}"
    endpoint_config_name = f"hail-damage-config-{timestamp}"
    endpoint_name = f"hail-damage-endpoint-{timestamp}"
    
    # Create model
    print(f"📦 Creating model: {model_name}")
    sm.create_model(
        ModelName=model_name,
        ExecutionRoleArn=args.role,
        PrimaryContainer={
            'Image': '763104351884.dkr.ecr.us-east-2.amazonaws.com/pytorch-inference:2.0.1-gpu-py310',
            'ModelDataUrl': f's3://{args.bucket}/{args.model_prefix}/output/model.tar.gz'
        }
    )
    
    # Create endpoint configuration
    print(f"⚙️ Creating endpoint config: {endpoint_config_name}")
    sm.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[{
            'VariantName': 'AllTraffic',
            'ModelName': model_name,
            'InitialInstanceCount': 1,
            'InstanceType': 'ml.g4dn.xlarge'
        }]
    )
    
    # Create endpoint
    print(f"🚀 Creating endpoint: {endpoint_name}")
    sm.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    
    print("⏳ Waiting for endpoint to be in service...")
    waiter = sm.get_waiter('endpoint_in_service')
    waiter.wait(EndpointName=endpoint_name)
    
    print(f"✅ Endpoint deployed successfully: {endpoint_name}")
    print(f"🔗 Use this endpoint name for inference: {endpoint_name}")

if __name__ == "__main__":
    main()

