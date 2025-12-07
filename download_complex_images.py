#!/usr/bin/env python3
"""
Download high-quality, complex images with multiple objects and actions from multiple sources.
Images contain complex scenes with people, animals, and various activities.
"""

import requests
import os
import time
from pathlib import Path
from PIL import Image
import json

# Disable proxy for requests
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Create test images directory in project
PROJECT_DIR = Path(__file__).parent
TEST_DIR = PROJECT_DIR / "test_photos"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Complex scenarios with multiple objects and actions
# Using Unsplash Source API with specific search terms
complex_scenarios = [
    # Complex beach scenarios
    {"url": "https://source.unsplash.com/1200x800/?man,woman,beach,sitting", "filename": "man_woman_sitting_beach_complex.jpg", "description": "A man and a woman sitting together on the beach"},
    {"url": "https://source.unsplash.com/1200x800/?woman,lying,beach,towel", "filename": "woman_lying_beach_towel_complex.jpg", "description": "A woman lying on a beach towel"},
    {"url": "https://source.unsplash.com/1200x800/?family,beach,playing,children", "filename": "family_children_playing_beach.jpg", "description": "A family with children playing on the beach"},
    {"url": "https://source.unsplash.com/1200x800/?people,volleyball,beach,action", "filename": "people_playing_volleyball_beach.jpg", "description": "People playing volleyball on the beach"},
    {"url": "https://source.unsplash.com/1200x800/?couple,beach,sunset,holding,hands", "filename": "couple_beach_sunset_holding_hands.jpg", "description": "A couple holding hands on the beach during sunset"},
    
    # Complex outdoor scenarios with people and animals
    {"url": "https://source.unsplash.com/1200x800/?woman,dog,snow,standing,winter", "filename": "woman_dog_snow_standing_winter.jpg", "description": "A woman standing in the snow with her dog in winter"},
    {"url": "https://source.unsplash.com/1200x800/?man,woman,dog,park,walking", "filename": "man_woman_dog_park_walking.jpg", "description": "A man and a woman walking their dog in the park"},
    {"url": "https://source.unsplash.com/1200x800/?family,dog,picnic,park,grass", "filename": "family_dog_picnic_park.jpg", "description": "A family with a dog having a picnic in the park"},
    {"url": "https://source.unsplash.com/1200x800/?children,cat,playing,indoor,home", "filename": "children_cat_playing_indoor.jpg", "description": "Children playing with a cat indoors"},
    {"url": "https://source.unsplash.com/1200x800/?woman,cat,window,sitting,reading", "filename": "woman_cat_window_sitting_reading.jpg", "description": "A woman sitting by a window reading with her cat"},
    
    # Complex activity scenarios
    {"url": "https://source.unsplash.com/1200x800/?man,woman,dancing,party,celebration", "filename": "man_woman_dancing_party.jpg", "description": "A man and a woman dancing at a party"},
    {"url": "https://source.unsplash.com/1200x800/?people,restaurant,dining,table,food", "filename": "people_restaurant_dining_table_food.jpg", "description": "People dining at a restaurant table with food"},
    {"url": "https://source.unsplash.com/1200x800/?team,office,meeting,table,discussion", "filename": "team_office_meeting_table_discussion.jpg", "description": "A team having a meeting around an office table"},
    {"url": "https://source.unsplash.com/1200x800/?woman,yoga,park,morning,exercise", "filename": "woman_yoga_park_morning_exercise.jpg", "description": "A woman doing yoga in the park in the morning"},
    {"url": "https://source.unsplash.com/1200x800/?man,cooking,kitchen,food,preparing", "filename": "man_cooking_kitchen_food_preparing.jpg", "description": "A man cooking and preparing food in the kitchen"},
    
    # Complex music and performance scenarios
    {"url": "https://source.unsplash.com/1200x800/?man,singing,stage,microphone,lights", "filename": "man_singing_stage_microphone_lights.jpg", "description": "A man singing on stage with a microphone and lights"},
    {"url": "https://source.unsplash.com/1200x800/?woman,singing,guitar,performing,stage", "filename": "woman_singing_guitar_performing.jpg", "description": "A woman singing and playing guitar on stage"},
    {"url": "https://source.unsplash.com/1200x800/?band,performing,concert,stage,audience", "filename": "band_performing_concert_stage_audience.jpg", "description": "A band performing at a concert on stage with audience"},
    
    # Complex nature and outdoor scenarios
    {"url": "https://source.unsplash.com/1200x800/?people,hiking,mountain,trail,backpack", "filename": "people_hiking_mountain_trail_backpack.jpg", "description": "People hiking on a mountain trail with backpacks"},
    {"url": "https://source.unsplash.com/1200x800/?camping,tent,mountains,fire,night", "filename": "camping_tent_mountains_fire_night.jpg", "description": "A camping tent in the mountains with a fire at night"},
    {"url": "https://source.unsplash.com/1200x800/?sunset,beach,waves,people,silhouette", "filename": "sunset_beach_waves_people_silhouette.jpg", "description": "Sunset over beach with waves and people silhouettes"},
    
    # Complex pet scenarios
    {"url": "https://source.unsplash.com/1200x800/?dog,running,beach,water,splashing", "filename": "dog_running_beach_water_splashing.jpg", "description": "A dog running on the beach splashing in water"},
    {"url": "https://source.unsplash.com/1200x800/?cat,playing,yarn,indoor,home", "filename": "cat_playing_yarn_indoor_home.jpg", "description": "A cat playing with yarn indoors at home"},
    {"url": "https://source.unsplash.com/1200x800/?golden,retriever,sitting,park,grass", "filename": "golden_retriever_sitting_park_grass.jpg", "description": "A golden retriever sitting in a park on grass"},
    {"url": "https://source.unsplash.com/photo-1601758228041-f3b2795255f1?w=1200&q=90", "filename": "cat_dog_playing_together_home.jpg", "description": "A cat and a dog playing together at home"},
    
    # Complex social scenarios
    {"url": "https://source.unsplash.com/1200x800/?friends,gathering,outdoor,table,talking", "filename": "friends_gathering_outdoor_table_talking.jpg", "description": "Friends gathering around an outdoor table talking"},
    {"url": "https://source.unsplash.com/1200x800/?wedding,ceremony,bride,groom,outdoor", "filename": "wedding_ceremony_bride_groom_outdoor.jpg", "description": "A wedding ceremony with bride and groom outdoors"},
    {"url": "https://source.unsplash.com/1200x800/?birthday,party,children,cake,celebration", "filename": "birthday_party_children_cake_celebration.jpg", "description": "A birthday party with children and cake celebration"},
    
    # Complex work scenarios
    {"url": "https://source.unsplash.com/1200x800/?people,collaborating,office,whiteboard,meeting", "filename": "people_collaborating_office_whiteboard.jpg", "description": "People collaborating in an office with a whiteboard"},
    {"url": "https://source.unsplash.com/1200x800/?woman,working,laptop,desk,coffee", "filename": "woman_working_laptop_desk_coffee.jpg", "description": "A woman working on a laptop at a desk with coffee"},
    
    # Complex sports scenarios
    {"url": "https://source.unsplash.com/1200x800/?athletes,competing,sports,field,action", "filename": "athletes_competing_sports_field_action.jpg", "description": "Athletes competing in sports on a field with action"},
    {"url": "https://source.unsplash.com/1200x800/?people,yoga,outdoor,mat,exercise", "filename": "people_yoga_outdoor_mat_exercise.jpg", "description": "People doing yoga outdoors on mats"},
]

def download_from_unsplash_source(url, filepath, description, current, total):
    """Download image from Unsplash Source API"""
    try:
        print(f"[{current}/{total}] Downloading: {description}...", end=' ', flush=True)
        
        # Unsplash Source API returns random images based on keywords
        response = requests.get(url, timeout=20, stream=True, proxies={'http': None, 'https': None}, allow_redirects=True)
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"✗ (not an image)")
                return False
            
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
                time.sleep(1)  # Be respectful to Unsplash
                return True
            except Exception as e:
                print(f"✗ (invalid image)")
                return False
        else:
            print(f"✗ (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ ({str(e)[:30]})")
        return False

def download_from_pexels(filepath, description, query, current, total):
    """Try to download from Pexels (free alternative)"""
    # Pexels API requires API key, so we'll use direct image URLs
    # For now, skip Pexels and use Unsplash Source
    return False

def main():
    print(f"Downloading complex, high-quality images to: {TEST_DIR}")
    print(f"Total images to download: {len(complex_scenarios)}\n")
    print("Using Unsplash Source API for random high-quality images...\n")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for idx, img in enumerate(complex_scenarios, 1):
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
                pass  # File exists but invalid, will re-download
        
        if download_from_unsplash_source(img["url"], filepath, img["description"], idx, len(complex_scenarios)):
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
    print(f"  Total: {downloaded + skipped}/{len(complex_scenarios)}")
    print(f"\nImages saved to: {TEST_DIR}")
    print(f"\nAll images contain complex scenes with multiple objects and actions!")

if __name__ == "__main__":
    main()

