#!/usr/bin/env python3
import argparse
import boto3
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--data-prefix', required=True)
    parser.add_argument('--model-output', required=True)
    parser.add_argument('--image-uri', required=True)
    args = parser.parse_args()
    
    print("🏗️ Setting up YOLOv8 training job...")
    print(f"📦 Container: {args.image_uri}")
    print(f"📂 Data: s3://{args.bucket}/{args.data_prefix}")
    print(f"📂 Output: s3://{args.bucket}/{args.model_output}")
    
    # Create SageMaker client
    sm = boto3.client('sagemaker', region_name='us-east-2')
    
    # Generate unique job name
    job_name = f"yolo-hail-damage-{int(time.time())}"
    
    # Training job configuration
    training_config = {
        'TrainingJobName': job_name,
        'AlgorithmSpecification': {
            'TrainingImage': args.image_uri,
            'TrainingInputMode': 'File'
        },
        'RoleArn': args.role,
        'InputDataConfig': [{
            'ChannelName': 'training',
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': f's3://{args.bucket}/{args.data_prefix}',
                    'S3DataDistributionType': 'FullyReplicated'
                }
            },
            'ContentType': 'application/x-yaml',
            'CompressionType': 'None'
        }],
        'OutputDataConfig': {
            'S3OutputPath': f's3://{args.bucket}/{args.model_output}'
        },
        'ResourceConfig': {
            'InstanceType': 'ml.p3.2xlarge',  # GPU for training
            'InstanceCount': 1,
            'VolumeSizeInGB': 100
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 24 * 3600  # 24 hours max
        },
        'HyperParameters': {
            'epochs': '100',
            'batch-size': '8', 
            'img-size': '640',
            'model-name': 'hail-damage-detector'
        }
    }
    
    # Start training job
    print(f"🚀 Starting training job: {job_name}")
    sm.create_training_job(**training_config)
    
    # Wait for completion
    print("⏳ Waiting for training to complete...")
    waiter = sm.get_waiter('training_job_completed_or_stopped')
    waiter.wait(TrainingJobName=job_name)
    
    # Check final status
    response = sm.describe_training_job(TrainingJobName=job_name)
    status = response['TrainingJobStatus']
    
    if status == 'Completed':
        print("✅ Training completed successfully!")
        print(f"📦 Model artifacts: {response['ModelArtifacts']['S3ModelArtifacts']}")
    else:
        print(f"❌ Training failed with status: {status}")
        if 'FailureReason' in response:
            print(f"💥 Failure reason: {response['FailureReason']}")

if __name__ == "__main__":
    main()

