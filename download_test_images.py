#!/usr/bin/env python3
"""
Download 50+ test images from Unsplash for testing the photo search application.
Images include complex scenarios with people in various activities and backgrounds.
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

# 50+ diverse test images with complex scenarios
test_images = [
    # Beach and water activities
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", "filename": "woman_lying_beach.jpg", "description": "Woman lying on beach"},
    {"url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&q=80", "filename": "people_beach_swimming.jpg", "description": "People swimming at beach"},
    {"url": "https://images.unsplash.com/photo-1519046904884-53103b34bcc1?w=800&q=80", "filename": "beach_sunset_people.jpg", "description": "People at beach during sunset"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "woman_beach_towel.jpg", "description": "Woman on beach with towel"},
    {"url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80", "filename": "people_beach_volleyball.jpg", "description": "People playing volleyball on beach"},
    
    # Music and singing
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "filename": "man_singing_microphone.jpg", "description": "Man singing with microphone"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80", "filename": "woman_singing_stage.jpg", "description": "Woman singing on stage"},
    {"url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80", "filename": "band_performing.jpg", "description": "Band performing music"},
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "filename": "singer_concert.jpg", "description": "Singer at concert"},
    {"url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=800&q=80", "filename": "man_guitar_singing.jpg", "description": "Man playing guitar and singing"},
    
    # Sports and activities
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80", "filename": "people_basketball.jpg", "description": "People playing basketball"},
    {"url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80", "filename": "woman_running.jpg", "description": "Woman running"},
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80", "filename": "people_soccer.jpg", "description": "People playing soccer"},
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80", "filename": "man_cycling.jpg", "description": "Man cycling"},
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80", "filename": "people_yoga.jpg", "description": "People doing yoga"},
    
    # Food and dining
    {"url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80", "filename": "people_restaurant_dining.jpg", "description": "People dining in restaurant"},
    {"url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80", "filename": "people_cafe_coffee.jpg", "description": "People in cafe drinking coffee"},
    {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80", "filename": "chef_cooking.jpg", "description": "Chef cooking in kitchen"},
    {"url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80", "filename": "people_bar_drinking.jpg", "description": "People at bar drinking"},
    {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80", "filename": "family_dinner.jpg", "description": "Family having dinner"},
    
    # Work and office
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80", "filename": "people_office_meeting.jpg", "description": "People in office meeting"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80", "filename": "woman_working_laptop.jpg", "description": "Woman working on laptop"},
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80", "filename": "man_presentation.jpg", "description": "Man giving presentation"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80", "filename": "people_collaborating.jpg", "description": "People collaborating at work"},
    
    # Nature and outdoor
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "people_mountain_hiking.jpg", "description": "People hiking in mountains"},
    {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=800&q=80", "filename": "woman_camping.jpg", "description": "Woman camping outdoors"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "people_picnic_park.jpg", "description": "People having picnic in park"},
    {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=800&q=80", "filename": "man_fishing.jpg", "description": "Man fishing"},
    {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "filename": "people_forest_walking.jpg", "description": "People walking in forest"},
    
    # Urban and city
    {"url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80", "filename": "person_city_street.jpg", "description": "Person on city street"},
    {"url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80", "filename": "woman_urban_background.jpg", "description": "Woman with urban background"},
    {"url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80", "filename": "people_shopping.jpg", "description": "People shopping"},
    {"url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80", "filename": "man_subway.jpg", "description": "Man in subway"},
    
    # Social and events
    {"url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&q=80", "filename": "people_wedding.jpg", "description": "People at wedding"},
    {"url": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800&q=80", "filename": "birthday_party.jpg", "description": "Birthday party celebration"},
    {"url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&q=80", "filename": "people_dancing.jpg", "description": "People dancing"},
    {"url": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800&q=80", "filename": "friends_gathering.jpg", "description": "Friends gathering together"},
    
    # Portraits and lifestyle
    {"url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80", "filename": "woman_portrait_outdoor.jpg", "description": "Woman portrait outdoor"},
    {"url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80", "filename": "man_portrait_nature.jpg", "description": "Man portrait in nature"},
    {"url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&q=80", "filename": "woman_reading.jpg", "description": "Woman reading book"},
    {"url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80", "filename": "man_writing.jpg", "description": "Man writing"},
    
    # More diverse scenarios
    {"url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80", "filename": "people_beach_sunset_2.jpg", "description": "People at beach sunset"},
    {"url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&q=80", "filename": "people_cafe_2.jpg", "description": "People in cafe"},
    {"url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=800&q=80", "filename": "people_restaurant_2.jpg", "description": "People in restaurant"},
    {"url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&q=80", "filename": "person_nature_2.jpg", "description": "Person in nature"},
    {"url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80", "filename": "person_city_2.jpg", "description": "Person in city"},
    
    # Additional complex scenarios
    {"url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&q=80", "filename": "woman_beach_reading.jpg", "description": "Woman reading on beach"},
    {"url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=800&q=80", "filename": "people_mountain_camping.jpg", "description": "People camping in mountains"},
    {"url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", "filename": "beach_activities.jpg", "description": "Beach activities"},
    {"url": "https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&q=80", "filename": "people_water_sports.jpg", "description": "People doing water sports"},
    {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "filename": "musician_performing.jpg", "description": "Musician performing"},
    
    # More activities
    {"url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=800&q=80", "filename": "people_music_festival.jpg", "description": "People at music festival"},
    {"url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80", "filename": "band_concert.jpg", "description": "Band at concert"},
    {"url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80", "filename": "singer_stage_lights.jpg", "description": "Singer on stage with lights"},
    {"url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80", "filename": "athletes_competing.jpg", "description": "Athletes competing"},
    {"url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80", "filename": "woman_exercising.jpg", "description": "Woman exercising"},
    
    # More lifestyle
    {"url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80", "filename": "fine_dining.jpg", "description": "Fine dining restaurant"},
    {"url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80", "filename": "coffee_shop.jpg", "description": "Coffee shop scene"},
    {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80", "filename": "kitchen_cooking.jpg", "description": "Kitchen cooking scene"},
    {"url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80", "filename": "business_meeting.jpg", "description": "Business meeting"},
    {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80", "filename": "remote_working.jpg", "description": "Remote working"},
    
    # Cats and dogs
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&q=80", "filename": "cat_sitting.jpg", "description": "Cat sitting"},
    {"url": "https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=800&q=80", "filename": "cat_window.jpg", "description": "Cat looking out window"},
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800&q=80", "filename": "cat_playing.jpg", "description": "Cat playing"},
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800&q=80", "filename": "cat_sleeping.jpg", "description": "Cat sleeping"},
    {"url": "https://images.unsplash.com/photo-1571566882372-1598d88abd90?w=800&q=80", "filename": "cat_portrait.jpg", "description": "Cat portrait"},
    {"url": "https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=800&q=80", "filename": "cat_outdoor.jpg", "description": "Cat outdoors"},
    {"url": "https://images.unsplash.com/photo-1513245543132-31e50741706b?w=800&q=80", "filename": "cat_curious.jpg", "description": "Curious cat"},
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&q=80", "filename": "cat_black.jpg", "description": "Black cat"},
    {"url": "https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=800&q=80", "filename": "cat_white.jpg", "description": "White cat"},
    {"url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800&q=80", "filename": "cat_orange.jpg", "description": "Orange cat"},
    
    {"url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&q=80", "filename": "dog_sitting.jpg", "description": "Dog sitting"},
    {"url": "https://images.unsplash.com/photo-1534361960057-19889c4a8c3a?w=800&q=80", "filename": "dog_running.jpg", "description": "Dog running"},
    {"url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&q=80", "filename": "dog_playing.jpg", "description": "Dog playing"},
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80", "filename": "dog_beach.jpg", "description": "Dog at beach"},
    {"url": "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=800&q=80", "filename": "dog_park.jpg", "description": "Dog in park"},
    {"url": "https://images.unsplash.com/photo-1587300003388-59208cc962b6?w=800&q=80", "filename": "dog_portrait.jpg", "description": "Dog portrait"},
    {"url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&q=80", "filename": "dog_golden_retriever.jpg", "description": "Golden retriever dog"},
    {"url": "https://images.unsplash.com/photo-1534361960057-19889c4a8c3a?w=800&q=80", "filename": "dog_labrador.jpg", "description": "Labrador dog"},
    {"url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&q=80", "filename": "dog_puppy.jpg", "description": "Puppy dog"},
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80", "filename": "dog_playing_fetch.jpg", "description": "Dog playing fetch"},
    
    # Cats and dogs together
    {"url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&q=80", "filename": "cat_dog_together.jpg", "description": "Cat and dog together"},
    {"url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&q=80", "filename": "pets_playing.jpg", "description": "Pets playing together"},
    
    # ID cards, bank cards, and tickets with text information
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "id_card_sample.jpg", "description": "ID card with personal information"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "credit_card_sample.jpg", "description": "Credit card with card details"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "bank_card_sample.jpg", "description": "Bank card with account information"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "train_ticket_sample.jpg", "description": "Train ticket with travel details"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "boarding_pass.jpg", "description": "Boarding pass with flight information"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "driver_license.jpg", "description": "Driver license with personal details"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "passport_sample.jpg", "description": "Passport with identification information"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "event_ticket.jpg", "description": "Event ticket with details"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "receipt_sample.jpg", "description": "Receipt with transaction details"},
    {"url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80", "filename": "invoice_sample.jpg", "description": "Invoice with billing information"},
]

def download_image(url, filepath, description, current, total):
    """Download an image from URL and save to filepath"""
    try:
        print(f"[{current}/{total}] Downloading: {description}...", end=' ', flush=True)
        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓")
        return True
    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return False

def main():
    print(f"Downloading test images to: {TEST_DIR}")
    print(f"Total images to download: {len(test_images)}\n")
    
    downloaded = 0
    failed = 0
    skipped = 0
    
    for idx, img in enumerate(test_images, 1):
        filepath = TEST_DIR / img["filename"]
        # Skip if already exists
        if filepath.exists():
            skipped += 1
            continue
            
        if download_image(img["url"], filepath, img["description"], idx, len(test_images)):
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
    print(f"  Total: {downloaded + skipped}/{len(test_images)}")
    print(f"\nImages saved to: {TEST_DIR}")
    print(f"\nYou can now configure the photo search app to use:")
    print(f"  {TEST_DIR}")

if __name__ == "__main__":
    main()
