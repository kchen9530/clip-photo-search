#!/usr/bin/env python3
"""
Download high-quality, complex images with multiple objects and actions.
Uses multiple image sources and limits to 1000 images total.
"""

import requests
import os
import time
from pathlib import Path
from PIL import Image

# Completely disable all proxy settings
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

# Create test images directory
PROJECT_DIR = Path(__file__).parent
TEST_DIR = PROJECT_DIR / "test_photos"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Complex scenarios with specific Unsplash photo IDs (high quality, 1200px+)
# These are real photo IDs that match complex descriptions
complex_scenarios = [
    # Beach scenarios with multiple people and actions
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=90", "filename": "beach_people_sitting_complex.jpg", "description": "People sitting on the beach with umbrellas and towels"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=1200&q=90", "filename": "beach_family_playing_complex.jpg", "description": "Family playing on the beach with children"},
    {"url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=1200&q=90", "filename": "woman_lying_beach_complex.jpg", "description": "Woman lying on beach towel with sunglasses"},
    {"url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=90", "filename": "beach_volleyball_people_complex.jpg", "description": "People playing volleyball on beach with net"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=90", "filename": "beach_sunset_couple_complex.jpg", "description": "Couple on beach during sunset with waves"},
    
    # People with animals - complex scenarios
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=1200&q=90", "filename": "dog_beach_water_complex.jpg", "description": "Dog running on beach near water"},
    {"url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=1200&q=90", "filename": "dog_park_grass_complex.jpg", "description": "Dog playing in park on grass"},
    {"url": "https://images.unsplash.com/photo-1587300003388-59208cc962b6?w=1200&q=90", "filename": "dog_sitting_park_complex.jpg", "description": "Dog sitting in park with trees"},
    {"url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=1200&q=90", "filename": "dog_portrait_park_complex.jpg", "description": "Dog portrait in park setting"},
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=1200&q=90", "filename": "cat_playing_toy_complex.jpg", "description": "Cat playing with toy indoors"},
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=1200&q=90", "filename": "cat_sleeping_window_complex.jpg", "description": "Cat sleeping by window with sunlight"},
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=1200&q=90", "filename": "cat_sitting_window_complex.jpg", "description": "Cat sitting by window looking outside"},
    {"url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=1200&q=90", "filename": "cat_dog_together_complex.jpg", "description": "Cat and dog playing together"},
    
    # Music and performance - complex scenarios
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&q=90", "filename": "man_singing_stage_complex.jpg", "description": "Man singing on stage with microphone and lights"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1200&q=90", "filename": "woman_singing_mic_complex.jpg", "description": "Woman singing with microphone on stage"},
    {"url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=1200&q=90", "filename": "man_guitar_singing_complex.jpg", "description": "Man playing guitar and singing"},
    {"url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=90", "filename": "band_concert_stage_complex.jpg", "description": "Band performing at concert on stage"},
    
    # Restaurant and dining - complex scenarios
    {"url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=90", "filename": "restaurant_people_dining_complex.jpg", "description": "People dining in restaurant with food and drinks"},
    {"url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=90", "filename": "cafe_people_coffee_complex.jpg", "description": "People in cafe drinking coffee"},
    {"url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=90", "filename": "bar_people_drinking_complex.jpg", "description": "People drinking at bar with glasses"},
    
    # Office and work - complex scenarios
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1200&q=90", "filename": "office_team_meeting_complex.jpg", "description": "Team meeting in office around table"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=90", "filename": "woman_laptop_working_complex.jpg", "description": "Woman working on laptop at desk"},
    
    # Outdoor activities - complex scenarios
    {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=1200&q=90", "filename": "people_hiking_mountain_complex.jpg", "description": "People hiking on mountain trail"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=90", "filename": "camping_tent_mountain_complex.jpg", "description": "Camping tent in mountains"},
    
    # More complex scenarios with multiple objects and actions
    {"url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&q=90", "filename": "wedding_bride_groom_outdoor.jpg", "description": "Wedding ceremony with bride and groom outdoors"},
    {"url": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=1200&q=90", "filename": "birthday_party_children_cake.jpg", "description": "Birthday party with children and cake"},
    {"url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&q=90", "filename": "people_dancing_party_celebration.jpg", "description": "People dancing at a party celebration"},
    {"url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=1200&q=90", "filename": "people_cafe_talking_coffee.jpg", "description": "People talking in a cafe with coffee"},
    {"url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=1200&q=90", "filename": "people_restaurant_table_food.jpg", "description": "People at restaurant table with food"},
    {"url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=1200&q=90", "filename": "woman_reading_book_cafe.jpg", "description": "Woman reading a book in a cafe"},
    {"url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=90", "filename": "man_woman_city_walking.jpg", "description": "A man and a woman walking in the city"},
    {"url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=1200&q=90", "filename": "person_portrait_outdoor_nature.jpg", "description": "Person portrait outdoors in nature"},
    {"url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&q=90", "filename": "woman_running_park_morning.jpg", "description": "Woman running in park in the morning"},
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=90", "filename": "people_sports_playing_field.jpg", "description": "People playing sports on a field"},
    {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200&q=90", "filename": "chef_cooking_kitchen_food.jpg", "description": "Chef cooking food in kitchen"},
    {"url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200&q=90", "filename": "family_dinner_restaurant_table.jpg", "description": "Family having dinner at restaurant table"},
    {"url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=90", "filename": "beach_sunset_people_silhouette.jpg", "description": "Beach sunset with people silhouettes"},
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=90", "filename": "beach_people_umbrella_sitting.jpg", "description": "People sitting on beach with umbrellas"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=1200&q=90", "filename": "beach_family_children_playing.jpg", "description": "Family with children playing on beach"},
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=1200&q=90", "filename": "dog_beach_water_playing.jpg", "description": "Dog playing in water on beach"},
    {"url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=1200&q=90", "filename": "dog_park_grass_running.jpg", "description": "Dog running on grass in park"},
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=1200&q=90", "filename": "cat_playing_yarn_indoor.jpg", "description": "Cat playing with yarn indoors"},
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=1200&q=90", "filename": "cat_window_sunlight_sleeping.jpg", "description": "Cat sleeping by window in sunlight"},
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&q=90", "filename": "man_singing_microphone_stage.jpg", "description": "Man singing with microphone on stage"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1200&q=90", "filename": "woman_singing_mic_stage_lights.jpg", "description": "Woman singing with microphone on stage with lights"},
]

def download_image(url, filepath, description, current, total):
    """Download image from URL"""
    try:
        print(f"[{current}/{total}] {description[:50]}...", end=' ', flush=True)
        
        response = requests.get(
            url, 
            timeout=20, 
            stream=True,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
            proxies={'http': None, 'https': None, 'socks5': None, 'socks5h': None}
        )
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify image
            try:
                img = Image.open(filepath)
                width, height = img.size
                if width < 800 or height < 600:
                    print(f"⚠ ({width}x{height})")
                    return False
                print(f"✓ ({width}x{height})")
                time.sleep(0.3)
                return True
            except:
                print(f"✗ (invalid)")
                return False
        else:
            print(f"✗ ({response.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({str(e)[:20]})")
        return False

def get_existing_count():
    """Get count of existing images"""
    return len(list(TEST_DIR.glob("*.jpg")))

def main():
    max_images = 1000
    existing_count = get_existing_count()
    remaining_slots = max_images - existing_count
    
    print(f"📊 Current images: {existing_count}")
    print(f"📊 Remaining slots: {remaining_slots}")
    print(f"📊 Max limit: {max_images} images\n")
    
    if remaining_slots <= 0:
        print("⚠️  Already at 1000 image limit!")
        return
    
    images_to_download = complex_scenarios[:min(len(complex_scenarios), remaining_slots)]
    
    print(f"Downloading {len(images_to_download)} complex images...\n")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for idx, img in enumerate(images_to_download, 1):
        filepath = TEST_DIR / img["filename"]
        
        if filepath.exists():
            try:
                test_img = Image.open(filepath)
                width, height = test_img.size
                if width >= 800 and height >= 600:
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
    print(f"Summary:")
    print(f"  ✓ Downloaded: {downloaded}")
    print(f"  ⊘ Skipped: {skipped}")
    print(f"  ✗ Failed: {failed}")
    print(f"  📊 Total: {final_count}/{max_images}")
    print(f"\nImages: {TEST_DIR}")

if __name__ == "__main__":
    main()

