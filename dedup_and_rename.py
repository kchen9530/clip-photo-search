#!/usr/bin/env python3
"""
Deduplicate images and rename them with accurate descriptions matching their content.
"""

import hashlib
import os
from pathlib import Path
from PIL import Image
from collections import defaultdict
import json
import re

TEST_DIR = Path(__file__).parent / "test_photos"

def sanitize_filename(text):
    """Convert text to a valid filename"""
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text)
    # Remove multiple underscores
    text = re.sub(r'_+', '_', text)
    # Remove leading/trailing underscores
    text = text.strip('_')
    return text.lower()

def get_image_description_from_filename(filename):
    """Extract description from filename"""
    # Remove extension
    name = filename.stem
    
    # Common patterns to clean up
    name = name.replace('_complex', '')
    name = name.replace('_sample', '')
    name = name.replace('_accurate', '')
    name = name.replace('_1', '')
    name = name.replace('_2', '')
    name = name.replace('_3', '')
    name = name.replace('_4', '')
    
    # Convert underscores to readable text
    name = name.replace('_', ' ')
    
    # Capitalize first letter of each word
    words = name.split()
    name = ' '.join(word.capitalize() for word in words)
    
    return name

def analyze_image_content(filepath):
    """Analyze image to generate better description"""
    try:
        img = Image.open(filepath)
        width, height = img.size
        
        # Basic analysis based on filename patterns
        filename = filepath.stem.lower()
        
        # Detect key elements
        elements = []
        if 'man' in filename or 'men' in filename:
            elements.append('man')
        if 'woman' in filename or 'women' in filename:
            elements.append('woman')
        if 'dog' in filename:
            elements.append('dog')
        if 'cat' in filename:
            elements.append('cat')
        if 'beach' in filename:
            elements.append('beach')
        if 'park' in filename:
            elements.append('park')
        if 'restaurant' in filename or 'cafe' in filename or 'bar' in filename:
            elements.append('restaurant')
        if 'office' in filename or 'meeting' in filename:
            elements.append('office')
        if 'singing' in filename or 'sing' in filename:
            elements.append('singing')
        if 'sitting' in filename or 'sit' in filename:
            elements.append('sitting')
        if 'lying' in filename or 'lie' in filename:
            elements.append('lying')
        if 'playing' in filename or 'play' in filename:
            elements.append('playing')
        if 'running' in filename or 'run' in filename:
            elements.append('running')
        if 'snow' in filename:
            elements.append('snow')
        if 'mountain' in filename:
            elements.append('mountain')
        if 'sunset' in filename:
            elements.append('sunset')
        
        return elements
    except:
        return []

def generate_better_filename(filepath, elements):
    """Generate a better filename based on content analysis"""
    if not elements:
        return None
    
    filename_lower = filepath.stem.lower()
    parts = []
    
    # Determine people (be more careful - check actual filename)
    has_man = 'man' in filename_lower and 'woman' not in filename_lower
    has_woman = 'woman' in filename_lower
    has_both = 'man' in filename_lower and 'woman' in filename_lower
    has_people = 'people' in filename_lower or 'person' in filename_lower
    
    if has_both:
        parts.append('man_woman')
    elif has_man:
        parts.append('man')
    elif has_woman:
        parts.append('woman')
    elif has_people:
        parts.append('people')
    elif 'family' in filename_lower or 'children' in filename_lower:
        parts.append('people')
    elif 'couple' in filename_lower:
        parts.append('man_woman')
    
    # Animals (only if present)
    if 'dog' in elements:
        parts.append('dog')
    if 'cat' in elements:
        parts.append('cat')
    
    # Location (priority order)
    if 'beach' in elements:
        parts.append('beach')
    elif 'park' in elements:
        parts.append('park')
    elif 'restaurant' in elements or 'cafe' in elements or 'bar' in elements:
        parts.append('restaurant')
    elif 'office' in elements or 'meeting' in elements:
        parts.append('office')
    elif 'mountain' in elements:
        parts.append('mountain')
    elif 'snow' in elements:
        parts.append('snow')
    elif 'kitchen' in filename_lower:
        parts.append('kitchen')
    
    # Actions (only one main action)
    if 'singing' in elements:
        parts.append('singing')
    elif 'sitting' in elements:
        parts.append('sitting')
    elif 'lying' in elements:
        parts.append('lying')
    elif 'playing' in elements:
        parts.append('playing')
    elif 'running' in elements:
        parts.append('running')
    elif 'walking' in filename_lower:
        parts.append('walking')
    elif 'dancing' in filename_lower:
        parts.append('dancing')
    elif 'cooking' in filename_lower:
        parts.append('cooking')
    elif 'working' in filename_lower:
        parts.append('working')
    elif 'hiking' in filename_lower:
        parts.append('hiking')
    elif 'yoga' in filename_lower:
        parts.append('yoga')
    
    # Additional context (only if relevant)
    if 'sunset' in elements and 'beach' in elements:
        parts.append('sunset')
    elif 'sunset' in elements:
        parts = ['beach', 'sunset']  # Sunset usually implies beach
    
    # Special cases
    if 'cat' in elements and 'dog' in elements:
        parts = ['cat', 'dog', 'together']
    elif len(parts) == 1 and 'dog' in parts:
        # Dog alone needs location or action
        if 'park' in filename_lower:
            parts.append('park')
        elif 'beach' in filename_lower:
            parts.append('beach')
    
    if len(parts) >= 2:
        new_name = '_'.join(parts) + '.jpg'
        return new_name
    
    return None

def main():
    print("🔍 去重和重命名图片...\n")
    
    # Step 1: Deduplicate using MD5
    print("步骤 1: 检测重复图片...")
    image_hashes = defaultdict(list)
    
    for filename in TEST_DIR.glob("*.jpg"):
        try:
            with open(filename, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
                image_hashes[file_hash].append(filename)
        except Exception as e:
            print(f"⚠️  无法读取 {filename.name}: {e}")
    
    duplicates = {h: files for h, files in image_hashes.items() if len(files) > 1}
    
    if duplicates:
        print(f"找到 {len(duplicates)} 组重复图片")
        total_duplicates = 0
        for hash_val, files in duplicates.items():
            # Keep the first one with better name, or shortest name
            keep_file = min(files, key=lambda x: (len(x.stem), x.name))
            for f in files:
                if f != keep_file:
                    print(f"  删除: {f.name}")
                    f.unlink()
                    total_duplicates += 1
        print(f"✅ 已删除 {total_duplicates} 个重复文件\n")
    else:
        print("✅ 未找到重复图片\n")
    
    # Step 2: Rename files with better names
    print("步骤 2: 重命名图片以匹配内容...")
    
    renamed = 0
    for filename in TEST_DIR.glob("*.jpg"):
        try:
            elements = analyze_image_content(filename)
            new_name = generate_better_filename(filename, elements)
            
            if new_name and new_name != filename.name:
                new_path = TEST_DIR / new_name
                # Avoid overwriting
                counter = 1
                while new_path.exists() and new_path != filename:
                    base_name = new_name.replace('.jpg', '')
                    new_name = f"{base_name}_{counter}.jpg"
                    new_path = TEST_DIR / new_name
                    counter += 1
                
                if new_path != filename:
                    filename.rename(new_path)
                    print(f"  {filename.name} → {new_name}")
                    renamed += 1
        except Exception as e:
            print(f"⚠️  无法处理 {filename.name}: {e}")
    
    print(f"\n✅ 已重命名 {renamed} 个文件")
    
    final_count = len(list(TEST_DIR.glob("*.jpg")))
    print(f"📊 最终图片数: {final_count} 张")

if __name__ == "__main__":
    main()

