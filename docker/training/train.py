#!/usr/bin/env python3
import os
import argparse
import json
import sys
from pathlib import Path

print("🚀 Starting YOLOv8 Training Container")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Import training dependencies
try:
    from ultralytics import YOLO
    import mlflow
    import mlflow.pytorch
    import torch
    print("✅ Training imports successful")
    print(f"🔥 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU device: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def parse_hyperparameters():
    """Parse SageMaker hyperparameters"""
    hyperparams_path = '/opt/ml/input/config/hyperparameters.json'
    
    # Default hyperparameters (matching your Colab)
    defaults = {
        'epochs': 100,
        'batch-size': 8,
        'img-size': 640,
        'model-name': 'hail-damage-detector'
    }
    
    if os.path.exists(hyperparams_path):
        with open(hyperparams_path, 'r') as f:
            hyperparams = json.load(f)
            print("📋 Loaded hyperparameters from SageMaker:")
            for key, value in hyperparams.items():
                print(f"  {key}: {value}")
        
        # Update defaults with SageMaker hyperparams
        for key in defaults:
            if key in hyperparams:
                if key in ['epochs', 'batch-size', 'img-size']:
                    defaults[key] = int(hyperparams[key])
                else:
                    defaults[key] = hyperparams[key]
    else:
        print("📋 Using default hyperparameters")
    
    return defaults

def list_directory_contents(directory):
    """List directory contents for debugging"""
    print(f"📁 Contents of {directory}:")
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Limit to first 10 files per directory
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({file_size} bytes)")
            if len(files) > 10:
                print(f"{subindent}... and {len(files) - 10} more files")
    else:
        print(f"❌ Directory {directory} does not exist")

def main():
    # Parse hyperparameters
    hyperparams = parse_hyperparameters()
    
    # SageMaker paths
    input_dir = '/opt/ml/input/data/training'
    model_dir = '/opt/ml/model'
    
    print(f"📂 Input directory: {input_dir}")
    print(f"📂 Model output directory: {model_dir}")
    
    # Create model directory
    os.makedirs(model_dir, exist_ok=True)
    
    # List input contents
    list_directory_contents(input_dir)
    
    # Find data.yaml file
    data_yaml_candidates = [
        os.path.join(input_dir, 'data.yaml'),
        os.path.join(input_dir, 'dataset.yaml'),
    ]
    
    data_yaml = None
    for candidate in data_yaml_candidates:
        if os.path.exists(candidate):
            data_yaml = candidate
            break
    
    if not data_yaml:
        print("❌ ERROR: data.yaml not found!")
        print("Available files in input directory:")
        list_directory_contents(input_dir)
        sys.exit(1)
    
    print(f"📄 Using dataset config: {data_yaml}")
    
    # Display data.yaml content (exactly like your Colab)
    with open(data_yaml, 'r') as f:
        yaml_content = f.read()
        print("📄 Training with data.yaml:")
        print(yaml_content)
    
    # Start MLflow experiment tracking
    print("📊 Setting up MLflow tracking...")
    try:
        mlflow.set_experiment("hail-damage-detection")
        print("✅ MLflow experiment set")
    except Exception as e:
        print(f"⚠️ MLflow setup warning: {e}")
    
    # Start MLflow run
    with mlflow.start_run():
        # Log hyperparameters
        mlflow.log_params({
            'epochs': hyperparams['epochs'],
            'batch_size': hyperparams['batch-size'],
            'img_size': hyperparams['img-size'],
            'model_name': hyperparams['model-name'],
            'data_yaml_path': data_yaml
        })
        
        # Load YOLOv8 model (exactly like your Colab)
        print("🤖 Loading YOLOv8 model...")
        try:
            model = YOLO("yolov8n.pt")  # Download pretrained model
            print("✅ YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load YOLOv8: {e}")
            sys.exit(1)
        
        # Train the model (matching your Colab exactly)
        print("🚀 Starting training...")
        try:
            results = model.train(
                data=data_yaml,
                epochs=hyperparams['epochs'],
                imgsz=hyperparams['img-size'],
                batch=hyperparams['batch-size'],
                name=hyperparams['model-name'],
                project=model_dir,
                save=True,
                save_period=10,  # Save checkpoint every 10 epochs
                device=0 if torch.cuda.is_available() else 'cpu'
            )
            print("✅ Training completed successfully!")
        except Exception as e:
            print(f"❌ Training failed: {e}")
            sys.exit(1)
        
        # Log metrics to MLflow
        try:
            if hasattr(results, 'results_dict'):
                metrics = results.results_dict
                mlflow.log_metrics({
                    'final_mAP50': float(metrics.get('metrics/mAP50(B)', 0)),
                    'final_mAP50-95': float(metrics.get('metrics/mAP50-95(B)', 0)),
                    'precision': float(metrics.get('metrics/precision(B)', 0)),
                    'recall': float(metrics.get('metrics/recall(B)', 0))
                })
        except Exception as e:
            print(f"⚠️ MLflow metrics logging warning: {e}")
        
        # Save model artifacts
        model_artifacts_path = os.path.join(model_dir, hyperparams['model-name'])
        best_model_path = os.path.join(model_artifacts_path, 'weights', 'best.pt')
        last_model_path = os.path.join(model_artifacts_path, 'weights', 'last.pt')
        
        if os.path.exists(best_model_path):
            print(f"✅ Best model saved: {best_model_path}")
            try:
                mlflow.log_artifact(best_model_path, "model_weights")
            except Exception as e:
                print(f"⚠️ MLflow artifact logging warning: {e}")
        
        if os.path.exists(last_model_path):
            print(f"✅ Last model saved: {last_model_path}")
        
        # List final model directory
        list_directory_contents(model_dir)
        
        print("🎉 Training pipeline completed successfully!")

if __name__ == "__main__":
    main()

