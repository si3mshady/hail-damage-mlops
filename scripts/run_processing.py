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
    print(f"📦 Container URI: {args.image_uri}")
    print(f"📂 Input Prefix: s3://{args.bucket}/{args.input_prefix}")
    print(f"📂 Output Prefix: s3://{args.bucket}/{args.output_prefix}")
    
    session = Session()
    processor = ScriptProcessor(
        image_uri=args.image_uri,
        command=['python3'],
        role=args.role,
        instance_count=1,
        instance_type='ml.g4dn.xlarge',
        volume_size_in_gb=100,
        max_runtime_in_seconds=3600,
        sagemaker_session=session
    )
    
    job_name = f"autodistill-{int(time.time())}"
    print(f"🚀 Starting processing job: {job_name}")
    
    processor.run(
        code='docker/autodistill/process.py',   # <-- point to local repo path
        source_dir='docker/autodistill',         # <-- upload entire folder
        job_name=job_name,
        inputs=[ProcessingInput(
            source=f's3://{args.bucket}/{args.input_prefix}',
            destination='/opt/ml/processing/input')],
        outputs=[ProcessingOutput(
            source='/opt/ml/processing/output',
            destination=f's3://{args.bucket}/{args.output_prefix}')],
        wait=True,
        logs=True
    )
    
    print("✅ Autodistill processing completed successfully!")

if __name__ == "__main__":
    main()

