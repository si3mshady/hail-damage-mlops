#!/usr/bin/env python3
import os
import subprocess
import glob
import sys
from pathlib import Path

print("🚀 Starting Autodistill Processing Container")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Import after environment setup
try:
    from autodistill.detection import CaptionOntology
    from autodistill_grounded_sam import GroundedSAM
    print("✅ Autodistill imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def convert_png_to_jpg(input_dir):
    """Convert PNG files to JPG format"""
    print(f"🔄 Converting PNG files in {input_dir}")
    png_files = glob.glob(os.path.join(input_dir, "*.png"))
    converted_count = 0
    
    for png_file in png_files:
        jpg_file = png_file.replace('.png', '.jpg')
        try:
            # Use ImageMagick convert command
            result = subprocess.run(['convert', png_file, jpg_file], 
                                  capture_output=True, text=True, check=True)
            os.remove(png_file)
            converted_count += 1
            print(f"✅ Converted: {os.path.basename(png_file)} → {os.path.basename(jpg_file)}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to convert {png_file}: {e}")
            continue
    
    print(f"✅ Converted {converted_count} PNG files to JPG")
    return converted_count

def list_directory_contents(directory):
    """List all files in directory for debugging"""
    print(f"📁 Contents of {directory}:")
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({file_size} bytes)")
    else:
        print(f"❌ Directory {directory} does not exist")

def main():
    # SageMaker paths
    input_dir = '/opt/ml/processing/input'
    output_dir = '/opt/ml/processing/output'
    
    print(f"📂 Input directory: {input_dir}")
    print(f"📂 Output directory: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # List input contents
    list_directory_contents(input_dir)
    
    # Check if input directory has files
    if not os.path.exists(input_dir) or not os.listdir(input_dir):
        print("❌ No input files found!")
        sys.exit(1)
    
    # Step 1: Convert PNG to JPG (exactly like your Colab)
    convert_png_to_jpg(input_dir)
    
    # Step 2: Define ontology for hail damage (matches your Colab)
    print("🏷️ Setting up ontology for hail damage detection")
    ontology = CaptionOntology({
        "damaged roof shingles": "damage",
    })
    
    # Step 3: Load GroundedSAM model
    print("🤖 Loading GroundedSAM model...")
    try:
        base_model = GroundedSAM(ontology=ontology)
        print("✅ GroundedSAM model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load GroundedSAM: {e}")
        sys.exit(1)
    
    # Step 4: Auto-label all images
    print("🏷️ Starting auto-labeling process...")
    try:
        base_model.label(
            input_folder=input_dir,
            output_folder=output_dir
        )
        print("✅ Auto-labeling completed successfully!")
    except Exception as e:
        print(f"❌ Auto-labeling failed: {e}")
        sys.exit(1)
    
    # Step 5: Verify outputs
    list_directory_contents(output_dir)
    
    # Check for data.yaml
    data_yaml_path = os.path.join(output_dir, 'data.yaml')
    if os.path.exists(data_yaml_path):
        print("📄 Generated data.yaml contents:")
        with open(data_yaml_path, 'r') as f:
            content = f.read()
            print(content)
        
        # Verify train/val directories exist
        train_dir = os.path.join(output_dir, 'train')
        val_dir = os.path.join(output_dir, 'valid')
        
        if os.path.exists(train_dir) and os.path.exists(val_dir):
            train_images = len(glob.glob(os.path.join(train_dir, 'images', '*')))
            val_images = len(glob.glob(os.path.join(val_dir, 'images', '*')))
            print(f"📊 Dataset split: {train_images} training, {val_images} validation images")
        else:
            print("⚠️ Warning: train/valid directories not found")
    else:
        print("❌ ERROR: data.yaml not generated!")
        sys.exit(1)
    
    print("🎉 Autodistill processing completed successfully!")

if __name__ == "__main__":
    main()

