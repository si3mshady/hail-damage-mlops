#!/usr/bin/env python3
import argparse
import boto3
import time
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker import Session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', required=True)
    parser.add_argument('--bucket', required=True) 
    parser.add_argument('--input-prefix', required=True)
    parser.add_argument('--output-prefix', required=True)
    parser.add_argument('--image-uri', required=True)
    args = parser.parse_args()
    
    print("🏗️ Setting up Autodistill processing job...")
    print(f"📦 Container: {args.image_uri}")
    print(f"📂 Input: s3://{args.bucket}/{args.input_prefix}")
    print(f"📂 Output: s3://{args.bucket}/{args.output_prefix}")
    
    # Create SageMaker session
    session = Session()
    
    # Create processor with GPU instance for Autodistill
    processor = ScriptProcessor(
        image_uri=args.image_uri,
        role=args.role,
        instance_count=1,
        instance_type='ml.g4dn.xlarge',  # GPU instance for GroundedSAM
        volume_size_in_gb=100,
        max_runtime_in_seconds=3600,  # 1 hour timeout
        sagemaker_session=session
    )
    
    # Run processing job
    job_name = f"autodistill-{int(time.time())}"
    print(f"🚀 Starting processing job: {job_name}")
    
    processor.run(
        job_name=job_name,
        inputs=[ProcessingInput(
            source=f's3://{args.bucket}/{args.input_prefix}',
            destination='/opt/ml/processing/input',
            s3_data_type='S3Prefix',
            s3_input_mode='File'
        )],
        outputs=[ProcessingOutput(
            source='/opt/ml/processing/output',
            destination=f's3://{args.bucket}/{args.output_prefix}',
            s3_upload_mode='EndOfJob'
        )],
        wait=True,
        logs=True
    )
    
    print("✅ Autodistill processing completed successfully!")

if __name__ == "__main__":
    main()

