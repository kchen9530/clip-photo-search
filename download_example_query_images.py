#!/usr/bin/env python3
"""
Download additional test images based on example queries from the web interface.
"""

import requests
import os
import time
from pathlib import Path

# Disable proxy for requests
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Create test images directory in project
PROJECT_DIR = Path(__file__).parent
TEST_DIR = PROJECT_DIR / "test_photos"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Example queries from the web interface
example_queries_images = [
    # 女人躺在海滩上 (Woman lying on beach)
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", "filename": "woman_lying_beach_sand_1.jpg", "description": "Woman lying on beach sand"},
    {"url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&q=80", "filename": "woman_lying_beach_sand_2.jpg", "description": "Woman lying on beach with towel"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=800&q=80", "filename": "woman_lying_beach_sand_3.jpg", "description": "Woman relaxing lying on beach"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "woman_lying_beach_sand_4.jpg", "description": "Woman lying on beach during sunset"},
    
    # 男人在唱歌 (Man singing)
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "filename": "man_singing_stage_1.jpg", "description": "Man singing on stage"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80", "filename": "man_singing_mic_1.jpg", "description": "Man singing with microphone"},
    {"url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=800&q=80", "filename": "man_singing_guitar_1.jpg", "description": "Man singing while playing guitar"},
    {"url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80", "filename": "man_singing_concert_1.jpg", "description": "Man singing at concert"},
    
    # 猫在玩耍 (Cat playing)
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800&q=80", "filename": "cat_playing_toy_1.jpg", "description": "Cat playing with toy"},
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800&q=80", "filename": "cat_playing_ball_1.jpg", "description": "Cat playing with ball"},
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&q=80", "filename": "cat_playing_indoor_1.jpg", "description": "Cat playing indoors"},
    {"url": "https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=800&q=80", "filename": "cat_playing_outdoor_1.jpg", "description": "Cat playing outdoors"},
    
    # 狗在海滩 (Dog at beach)
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80", "filename": "dog_beach_playing_1.jpg", "description": "Dog playing at beach"},
    {"url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=800&q=80", "filename": "dog_beach_running_1.jpg", "description": "Dog running on beach"},
    {"url": "https://images.unsplash.com/photo-1587300003388-59208cc962b6?w=800&q=80", "filename": "dog_beach_sitting_1.jpg", "description": "Dog sitting at beach"},
    {"url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&q=80", "filename": "dog_beach_water_1.jpg", "description": "Dog at beach in water"},
    
    # 海滩日落 (Beach sunset)
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", "filename": "beach_sunset_scene_1.jpg", "description": "Beach sunset scene"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=800&q=80", "filename": "beach_sunset_scene_2.jpg", "description": "Beautiful beach sunset"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "beach_sunset_scene_3.jpg", "description": "Sunset over beach"},
    {"url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80", "filename": "beach_sunset_scene_4.jpg", "description": "Beach during sunset"},
    
    # 人们在餐厅 (People in restaurant)
    {"url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80", "filename": "people_restaurant_dining_1.jpg", "description": "People dining in restaurant"},
    {"url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80", "filename": "people_restaurant_dining_2.jpg", "description": "People eating at restaurant"},
    {"url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80", "filename": "people_restaurant_dining_3.jpg", "description": "People in restaurant setting"},
    {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80", "filename": "people_restaurant_dining_4.jpg", "description": "People at restaurant table"},
    
    # 办公室会议 (Office meeting)
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80", "filename": "office_meeting_people_1.jpg", "description": "People in office meeting"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80", "filename": "office_meeting_people_2.jpg", "description": "Office meeting discussion"},
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80", "filename": "office_meeting_people_3.jpg", "description": "Business meeting in office"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80", "filename": "office_meeting_people_4.jpg", "description": "Team meeting in office"},
]

def download_image(url, filepath, description, current, total):
    """Download an image from URL and save to filepath"""
    try:
        print(f"[{current}/{total}] Downloading: {description}...", end=' ', flush=True)
        response = requests.get(url, timeout=15, stream=True, proxies={'http': None, 'https': None})
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓")
        time.sleep(0.3)  # Be respectful
        return True
    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return False

def main():
    print(f"Downloading example query images to: {TEST_DIR}")
    print(f"Total images to download: {len(example_queries_images)}\n")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for idx, img in enumerate(example_queries_images, 1):
        filepath = TEST_DIR / img["filename"]
        # Skip if already exists
        if filepath.exists():
            skipped += 1
            continue
            
        if download_image(img["url"], filepath, img["description"], idx, len(example_queries_images)):
            downloaded += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Download Summary:")
    print(f"  ✓ Successfully downloaded: {downloaded}")
    if skipped > 0:
        print(f"  ⊘ Skipped (already exists): {skipped}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}")
    print(f"  Total: {downloaded + skipped}/{len(example_queries_images)}")
    print(f"\nImages saved to: {TEST_DIR}")

if __name__ == "__main__":
    main()

