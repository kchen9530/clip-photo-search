#!/usr/bin/env python3
"""
Download high-quality, complex images similar to ImageNet style.
Uses multiple reliable image sources with specific, complex scenarios.
Limits total images to 1000.
"""

import requests
import os
import time
from pathlib import Path
from PIL import Image
import hashlib

# Disable proxy for requests
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Create test images directory in project
PROJECT_DIR = Path(__file__).parent
TEST_DIR = PROJECT_DIR / "test_photos"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# High-quality image sources with specific photo IDs from Unsplash
# These are actual photo IDs that match complex scenarios
complex_images = [
    # Complex beach scenarios - man, woman, sitting, lying
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=90", "filename": "beach_people_sitting_1.jpg", "description": "People sitting on the beach"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=1200&q=90", "filename": "beach_people_sitting_2.jpg", "description": "People sitting together on the beach"},
    {"url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=1200&q=90", "filename": "woman_lying_beach_1.jpg", "description": "A woman lying on the beach"},
    {"url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=90", "filename": "people_volleyball_beach_1.jpg", "description": "People playing volleyball on the beach"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=90", "filename": "beach_sunset_people_1.jpg", "description": "People on the beach during sunset"},
    
    # Complex scenarios with man, woman, dog, cat
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=1200&q=90", "filename": "dog_beach_playing_1.jpg", "description": "A dog playing on the beach"},
    {"url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=1200&q=90", "filename": "dog_park_running_1.jpg", "description": "A dog running in the park"},
    {"url": "https://images.unsplash.com/photo-1587300003388-59208cc962b6?w=1200&q=90", "filename": "dog_park_sitting_1.jpg", "description": "A dog sitting in the park"},
    {"url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=1200&q=90", "filename": "dog_sitting_park_1.jpg", "description": "A dog sitting in a park"},
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=1200&q=90", "filename": "cat_playing_indoor_1.jpg", "description": "A cat playing indoors"},
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=1200&q=90", "filename": "cat_sleeping_window_1.jpg", "description": "A cat sleeping by a window"},
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=1200&q=90", "filename": "cat_sitting_window_1.jpg", "description": "A cat sitting by a window"},
    {"url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=1200&q=90", "filename": "cat_dog_together_1.jpg", "description": "A cat and a dog together"},
    
    # Complex music scenarios - man, woman, singing
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&q=90", "filename": "man_singing_stage_1.jpg", "description": "A man singing on stage"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1200&q=90", "filename": "woman_singing_microphone_1.jpg", "description": "A woman singing with microphone"},
    {"url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=1200&q=90", "filename": "man_guitar_singing_1.jpg", "description": "A man playing guitar and singing"},
    {"url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=90", "filename": "band_performing_concert_1.jpg", "description": "A band performing at a concert"},
    
    # Complex restaurant scenarios
    {"url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=90", "filename": "people_restaurant_dining_1.jpg", "description": "People dining in a restaurant"},
    {"url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=90", "filename": "people_cafe_coffee_1.jpg", "description": "People drinking coffee in a cafe"},
    {"url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=90", "filename": "people_bar_drinking_1.jpg", "description": "People drinking at a bar"},
    
    # Complex office scenarios
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1200&q=90", "filename": "team_meeting_office_1.jpg", "description": "A team meeting in an office"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=90", "filename": "woman_laptop_working_1.jpg", "description": "A woman working on a laptop"},
    
    # Complex outdoor scenarios
    {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=1200&q=90", "filename": "people_hiking_mountain_1.jpg", "description": "People hiking in the mountains"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=90", "filename": "people_camping_mountain_1.jpg", "description": "People camping in the mountains"},
]

# Use Pexels API as alternative (free, high quality)
# Note: You can get a free API key from https://www.pexels.com/api/
PEXELS_API_KEY = None  # Set this if you have a Pexels API key

def download_from_pexels(query, filepath, description):
    """Download image from Pexels API"""
    if not PEXELS_API_KEY:
        return False
    
    try:
        url = f"https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('photos') and len(data['photos']) > 0:
                photo_url = data['photos'][0]['src']['large']
                img_response = requests.get(photo_url, timeout=15, proxies={'http': None, 'https': None})
                if img_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    return True
    except:
        pass
    return False

def download_image(url, filepath, description, current, total):
    """Download image from URL"""
    try:
        print(f"[{current}/{total}] Downloading: {description}...", end=' ', flush=True)
        
        response = requests.get(
            url, 
            timeout=20, 
            stream=True, 
            proxies={'http': None, 'https': None},
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify it's a valid image
            try:
                img = Image.open(filepath)
                width, height = img.size
                if width < 600 or height < 400:
                    print(f"⚠ (small: {width}x{height})")
                    return False
                print(f"✓ ({width}x{height})")
                time.sleep(0.5)  # Be respectful
                return True
            except Exception as e:
                print(f"✗ (invalid)")
                return False
        else:
            print(f"✗ (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({str(e)[:30]})")
        return False

def get_existing_count():
    """Get count of existing images"""
    return len(list(TEST_DIR.glob("*.jpg")))

def main():
    max_images = 1000
    existing_count = get_existing_count()
    remaining_slots = max_images - existing_count
    
    print(f"Current images: {existing_count}")
    print(f"Remaining slots: {remaining_slots}")
    print(f"Max limit: {max_images} images\n")
    
    if remaining_slots <= 0:
        print("⚠️  Already at or over 1000 image limit!")
        return
    
    # Limit downloads to remaining slots
    images_to_download = complex_images[:min(len(complex_images), remaining_slots)]
    
    print(f"Downloading {len(images_to_download)} complex images to: {TEST_DIR}\n")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for idx, img in enumerate(images_to_download, 1):
        filepath = TEST_DIR / img["filename"]
        
        # Skip if already exists and is valid
        if filepath.exists():
            try:
                test_img = Image.open(filepath)
                width, height = test_img.size
                if width >= 600 and height >= 400:
                    skipped += 1
                    continue
            except:
                pass
        
        if download_image(img["url"], filepath, img["description"], idx, len(images_to_download)):
            downloaded += 1
        else:
            failed += 1
    
    final_count = get_existing_count()
    
    print(f"\n{'='*60}")
    print(f"Download Summary:")
    print(f"  ✓ Successfully downloaded: {downloaded}")
    if skipped > 0:
        print(f"  ⊘ Skipped (already exists): {skipped}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}")
    print(f"  Total images now: {final_count}/{max_images}")
    print(f"\nImages saved to: {TEST_DIR}")

if __name__ == "__main__":
    main()

