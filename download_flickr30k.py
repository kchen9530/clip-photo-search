#!/usr/bin/env python3
"""
Download Flickr30k dataset for testing.
This script downloads images from Flickr30k dataset.
"""

import requests
import os
import json
from pathlib import Path
from tqdm import tqdm
import shutil
import zipfile
import subprocess
import sys

# Disable proxy for requests
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Configuration
PROJECT_DIR = Path(__file__).parent
FLICKR30K_DIR = PROJECT_DIR / "flickr30k_images"
TEST_DIR = PROJECT_DIR / "test_photos"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Limit to 10000 images by default (can be changed via command line)
MAX_IMAGES = 10000

def download_file(url, filepath, description):
    """Download a file with progress bar"""
    try:
        print(f"Downloading {description}...")
        response = requests.get(url, stream=True, timeout=300, proxies={'http': None, 'https': None})
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=description) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        
        print(f"✅ {description} downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading {description}: {e}")
        return False

def extract_zip(zip_path, extract_to, max_images=None):
    """Extract zip file, optionally only first N images"""
    try:
        print(f"Verifying zip file: {zip_path.name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.testzip()
        
        # Get list of image files in zip
        image_extensions = ('.jpg', '.jpeg', '.png')
        image_files = [f for f in zip_ref.namelist() 
                       if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        if max_images and len(image_files) > max_images:
            print(f"Extracting first {max_images} images from {len(image_files)} total images...")
            image_files = sorted(image_files)[:max_images]
        else:
            print(f"Extracting {len(image_files)} images...")
        
        print(f"\n📦 Extracting {zip_path.name}...")
        print(f"   Extracting {len(image_files)} images (this may take a moment)...")
        extracted_count = 0
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for img_file in tqdm(image_files, desc="Extracting", unit="img", ncols=80):
                try:
                    zip_ref.extract(img_file, extract_to)
                    extracted_count += 1
                except Exception as e:
                    print(f"\n⚠️  Failed to extract {img_file}: {e}")
        
        print(f"\n✅ Extracted {extracted_count} images to {extract_to}")
        return True
    except zipfile.BadZipFile:
        print(f"❌ Zip file is corrupted, need to re-download")
        zip_path.unlink()
        return False
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        return False

def check_kaggle_installed():
    """Check if kaggle CLI is installed"""
    try:
        result = subprocess.run(['kaggle', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def download_via_kaggle():
    """Download Flickr30k using Kaggle API"""
    print("Attempting to download via Kaggle API...")
    
    if not check_kaggle_installed():
        print("❌ Kaggle CLI not found. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'kaggle'])
        except Exception as e:
            print(f"❌ Failed to install kaggle: {e}")
            return False
    
    # Check for Kaggle credentials
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if not kaggle_json.exists():
        print("⚠️  Kaggle credentials not found!")
        print("Please set up Kaggle API credentials:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Scroll to 'API' section and click 'Create New API Token'")
        print("3. This will download kaggle.json")
        print("4. Place it in ~/.kaggle/kaggle.json")
        print("\nAlternatively, you can download manually from:")
        print("https://www.kaggle.com/datasets/hsankesara/flickr-image-dataset")
        return False
    
    temp_dir = PROJECT_DIR / "temp_flickr30k"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download dataset using Kaggle API
        # Common dataset identifier for Flickr30k
        dataset = "hsankesara/flickr-image-dataset"
        
        print(f"Downloading dataset: {dataset}")
        print("📥 This may take a while. Download progress will be shown below...")
        print("=" * 60)
        
        # Run with real-time output to show progress
        result = subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', dataset, '-p', str(temp_dir)],
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n❌ Kaggle download failed. Trying alternative dataset...")
            print("=" * 60)
            # Try alternative dataset
            dataset = "adityajn105/flickr30k"
            print(f"Downloading alternative dataset: {dataset}")
            result = subprocess.run(
                ['kaggle', 'datasets', 'download', '-d', dataset, '-p', str(temp_dir)],
                text=True
            )
            
            if result.returncode != 0:
                print(f"\n❌ Alternative download also failed")
                return False
        
        print("=" * 60)
        print("✅ Download completed!")
        
        # Find downloaded zip file
        zip_files = list(temp_dir.glob("*.zip"))
        if not zip_files:
            print("❌ No zip file found after download")
            return False
        
        zip_path = zip_files[0]
        print(f"Found zip file: {zip_path.name}")
        
        # Extract images (only first MAX_IMAGES to save time)
        extract_dir = temp_dir / "flickr30k"
        if not extract_dir.exists() or len(list(extract_dir.rglob("*.jpg"))) == 0:
            print(f"Extracting only first {MAX_IMAGES} images to save time...")
            if not extract_zip(zip_path, temp_dir, max_images=MAX_IMAGES):
                return False
            # Rename if needed
            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir() and d.name != "flickr30k"]
            if extracted_dirs:
                extracted_dirs[0].rename(extract_dir)
        
        # Find images directory
        images_dir = None
        if (extract_dir / "flickr30k_images").exists():
            images_dir = extract_dir / "flickr30k_images"
        elif (extract_dir / "images").exists():
            images_dir = extract_dir / "images"
        elif any(extract_dir.glob("*.jpg")):
            images_dir = extract_dir
        else:
            # Search recursively
            for img_file in extract_dir.rglob("*.jpg"):
                images_dir = img_file.parent
                break
        
        if images_dir is None or not images_dir.exists():
            print("❌ Could not find images directory")
            return False
        
        print(f"Found images in: {images_dir}")
        return images_dir
        
    except Exception as e:
        print(f"❌ Error downloading via Kaggle: {e}")
        return False

def download_via_huggingface():
    """Download Flickr30k using Hugging Face datasets library"""
    print("Attempting to download via Hugging Face...")
    
    try:
        from datasets import load_dataset
    except ImportError:
        print("Installing datasets library...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'datasets', 'pillow'])
            from datasets import load_dataset
        except Exception as e:
            print(f"❌ Failed to install datasets library: {e}")
            return None
    
    temp_dir = PROJECT_DIR / "temp_flickr30k"
    temp_dir.mkdir(exist_ok=True)
    images_dir = temp_dir / "flickr30k_images"
    images_dir.mkdir(exist_ok=True)
    
    try:
        print("Loading Flickr30k dataset from Hugging Face (Streaming Mode)...")
        print(f"Downloading first {MAX_IMAGES} images...")
        
        # Try lmms-lab/flickr30k which is Parquet-based and supports streaming
        try:
            dataset = load_dataset("lmms-lab/flickr30k", split="test", streaming=True)
        except Exception as e:
            print(f"Primary HF dataset failed ({e}), trying backup...")
            # Fallback to another mirror if the first one fails
            dataset = load_dataset("nlphuji/flickr30k", split="test", streaming=True)
        
        # Download images
        downloaded_count = 0
        for i, item in enumerate(tqdm(dataset, total=MAX_IMAGES, desc="Downloading images")):
            if i >= MAX_IMAGES:
                break
            
            try:
                image = item['image']
                if image is not None:
                    # Save image
                    image_filename = f"{item.get('image_id', i):08d}.jpg"
                    image_path = images_dir / image_filename
                    image.save(image_path, "JPEG")
                    downloaded_count += 1
            except Exception as e:
                print(f"⚠️  Failed to download image {i}: {e}")
                continue
        
        if downloaded_count > 0:
            print(f"✅ Downloaded {downloaded_count} images to {images_dir}")
            return images_dir
        else:
            print("❌ No images were downloaded")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading via Hugging Face: {e}")
        print("This might be due to network issues or dataset availability.")
        return None

def download_via_direct_link():
    """Try to download from direct links (if available)"""
    print("Attempting direct download...")
    
    # Note: Direct links to Flickr30k are not always stable
    # These are example URLs that might work
    temp_dir = PROJECT_DIR / "temp_flickr30k"
    temp_dir.mkdir(exist_ok=True)
    
    # Common direct download URLs (may need to be updated)
    # Since direct links are not always available, we'll provide instructions
    print("⚠️  Direct download links for Flickr30k are not always available.")
    print("Please use one of these methods:")
    print("\n1. Hugging Face (Easiest - trying now):")
    print("   - Install: pip install datasets")
    print("   - Dataset: nlphuji/flickr30k")
    print("\n2. Kaggle (Recommended):")
    print("   - Install: pip install kaggle")
    print("   - Set up credentials: ~/.kaggle/kaggle.json")
    print("   - Download: kaggle datasets download -d hsankesara/flickr-image-dataset")
    print("\n3. Manual download:")
    print("   - Visit: https://www.kaggle.com/datasets/hsankesara/flickr-image-dataset")
    print("   - Or: https://www.kaggle.com/datasets/adityajn105/flickr30k")
    print("   - Extract images to: flickr30k_images/")
    
    return None

def process_flickr30k_images(images_dir):
    """Process and copy Flickr30k images to test_photos"""
    if not images_dir or not images_dir.exists():
        return False
    
    # Find all images
    all_images = sorted(list(images_dir.glob("*.jpg")))
    if len(all_images) == 0:
        # Try subdirectories
        all_images = sorted(list(images_dir.rglob("*.jpg")))
    
    print(f"\nFound {len(all_images)} images in {images_dir}")
    
    if len(all_images) == 0:
        print(f"❌ No images found in {images_dir}")
        return False
    
    # Clear existing test photos
    print("Clearing existing test photos...")
    existing_count = len(list(TEST_DIR.glob("*.jpg")))
    for old_file in TEST_DIR.glob("*.jpg"):
        old_file.unlink()
    print(f"Removed {existing_count} existing images")
    
    # Copy first MAX_IMAGES images
    print(f"\nCopying first {MAX_IMAGES} images to test_photos...")
    image_files = all_images[:MAX_IMAGES]
    
    copied_count = 0
    for idx, img_file in enumerate(tqdm(image_files, desc="Copying images")):
        dest = TEST_DIR / img_file.name
        try:
            shutil.copy2(img_file, dest)
            copied_count += 1
        except Exception as e:
            print(f"⚠️  Failed to copy {img_file.name}: {e}")
    
    print(f"✅ Copied {copied_count}/{len(image_files)} images to {TEST_DIR}")
    return True


def check_existing_images():
    """Check if images already exist in common locations"""
    from pathlib import Path
    PROJECT_DIR = Path(__file__).parent
    
    # Check flickr30k_images directory
    flickr_dir = PROJECT_DIR / "flickr30k_images"
    if flickr_dir.exists():
        images = list(flickr_dir.rglob("*.jpg"))
        if len(images) > 0:
            print(f"✅ Found {len(images)} existing images in {flickr_dir}")
            return flickr_dir
    
    # Check temp_flickr30k directory
    temp_dir = PROJECT_DIR / "temp_flickr30k"
    if temp_dir.exists():
        # Look for images in common subdirectories
        for subdir in ["flickr30k_images", "images", "flickr30k"]:
            check_dir = temp_dir / subdir
            if check_dir.exists():
                images = list(check_dir.rglob("*.jpg"))
                if len(images) > 0:
                    print(f"✅ Found {len(images)} existing images in {check_dir}")
                    return check_dir
        
        # Check root of temp directory
        images = list(temp_dir.rglob("*.jpg"))
        if len(images) > 0:
            print(f"✅ Found {len(images)} existing images in {temp_dir}")
            return temp_dir
    
    return None


def main():
    import argparse
    global MAX_IMAGES
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download Flickr30k dataset')
    parser.add_argument('--max-images', type=int, default=MAX_IMAGES,
                       help=f'Maximum number of images to download (default: {MAX_IMAGES})')
    args = parser.parse_args()
    
    MAX_IMAGES = args.max_images
    
    print("=" * 60)
    print("Downloading Flickr30k Dataset")
    print("=" * 60)
    print(f"Target: {MAX_IMAGES} images")
    print(f"Destination: {TEST_DIR}")
    print()
    
    images_dir = None
    
    # First, check if images already exist
    print("Checking for existing images...")
    images_dir = check_existing_images()
    
    # If no existing images, try downloading
    if not images_dir:
        # Try Hugging Face first (Fast Streaming)
        print("Method 1: Trying Hugging Face (Fast Streaming)...")
        images_dir = download_via_huggingface()
        
        # If Hugging Face fails, try Kaggle
        if not images_dir:
            print("\n" + "=" * 60)
            print("Hugging Face download failed. Trying Kaggle API...")
            print("=" * 60)
            images_dir = download_via_kaggle()
        
        # If both fail, provide instructions
        if not images_dir:
            print("\n" + "=" * 60)
            print("Automatic download not available. Trying alternative methods...")
            print("=" * 60)
            images_dir = download_via_direct_link()
    
    # If we have images, process them
    if images_dir:
        if process_flickr30k_images(images_dir):
            # Cleanup (but keep temp directory in case user wants to reuse)
            print("\n" + "=" * 60)
            print("✅ Successfully processed Flickr30k images!")
            print("=" * 60)
            print(f"📊 Final count: {len(list(TEST_DIR.glob('*.jpg')))} images")
            print(f"📁 Location: {TEST_DIR}")
            print("\n💡 You can now reindex the images in the backend!")
            return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  Automatic download not available")
        print("=" * 60)
        print("\nPlease download Flickr30k manually using one of these methods:")
        print("\nOption 1 - Kaggle (Recommended):")
        print("  1. Install: pip install kaggle")
        print("  2. Get API token from https://www.kaggle.com/account")
        print("  3. Place kaggle.json in ~/.kaggle/")
        print("  4. Run: kaggle datasets download -d hsankesara/flickr-image-dataset")
        print("  5. Extract the zip file")
        print("  6. Place images in: flickr30k_images/ or temp_flickr30k/flickr30k_images/")
        print("\nOption 2 - Manual Download:")
        print("  - Visit: https://www.kaggle.com/datasets/hsankesara/flickr-image-dataset")
        print("  - Download and extract")
        print("  - Place images in: flickr30k_images/ or temp_flickr30k/flickr30k_images/")
        print("\nOption 3 - Direct Copy:")
        print("  - If you already have Flickr30k images, place them in: flickr30k_images/")
        print("  - Then run this script again to process them")
        print("\nAfter placing images, run this script again to process them.")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
