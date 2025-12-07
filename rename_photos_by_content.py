#!/usr/bin/env python3
"""
Rename photos in test_photos directory based on their actual content using CLIP.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import torch
import clip
import re
from tqdm import tqdm

# Add backend to path to use CLIP model
sys.path.insert(0, str(Path(__file__).parent / "backend"))

TEST_DIR = Path(__file__).parent / "test_photos"

# Common descriptive prompts for CLIP
DESCRIPTIVE_PROMPTS = [
    "a photo of",
    "an image of",
    "a picture of",
    "a photograph of",
]

# Common scene/object categories to help generate better names
CATEGORY_PROMPTS = [
    "person", "people", "man", "woman", "child", "children",
    "dog", "cat", "pet", "animal",
    "beach", "ocean", "water", "park", "mountain", "forest", "city", "street",
    "restaurant", "cafe", "kitchen", "office", "room", "building",
    "food", "meal", "dish",
    "car", "vehicle", "bicycle", "bike",
    "sport", "playing", "running", "walking", "sitting", "standing",
    "sunset", "sunrise", "day", "night",
    "document", "paper", "card", "ticket", "receipt", "invoice",
    "indoor", "outdoor",
]

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

def generate_description_with_clip(model, preprocess, device, image_path):
    """Use CLIP to generate a description of the image"""
    try:
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        
        # Generate multiple candidate descriptions
        candidate_texts = []
        
        # Try different combinations
        for desc_prompt in DESCRIPTIVE_PROMPTS[:2]:  # Use first 2 to save time
            for category in CATEGORY_PROMPTS[:20]:  # Use first 20 categories
                candidate_texts.append(f"{desc_prompt} {category}")
        
        # Tokenize all candidates
        text_tokens = clip.tokenize(candidate_texts).to(device)
        
        with torch.no_grad():
            # Encode image and text
            image_features = model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            text_features = model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Compute similarities
            similarities = (image_features @ text_features.T).squeeze(0)
            
            # Get top 5 matches
            top_indices = similarities.argsort(descending=True)[:5]
            top_scores = similarities[top_indices]
            
            # Extract keywords from top matches
            keywords = []
            for idx in top_indices:
                text = candidate_texts[idx]
                # Extract the category word
                for cat in CATEGORY_PROMPTS:
                    if cat in text.lower():
                        if cat not in keywords:
                            keywords.append(cat)
                            break
                if len(keywords) >= 3:  # Get top 3 keywords
                    break
            
            # Build description from keywords
            if keywords:
                description = "_".join(keywords[:3])
                return description, float(top_scores[0].item())
        
        return "image", 0.0
        
    except Exception as e:
        print(f"⚠️  Error processing {image_path.name}: {e}")
        return None, 0.0

def generate_filename_from_description(description, original_name, index=0):
    """Generate a clean filename from description"""
    if not description or description == "image":
        # Fallback to numbered name
        ext = Path(original_name).suffix
        return f"photo_{index:04d}{ext}"
    
    # Sanitize description
    filename = sanitize_filename(description)
    
    # Add index if provided
    if index > 0:
        filename = f"{filename}_{index}"
    
    # Get original extension
    ext = Path(original_name).suffix
    return f"{filename}{ext}"

def main():
    print("=" * 60)
    print("Renaming Photos Based on Content")
    print("=" * 60)
    print()
    
    # Check if test_photos directory exists
    if not TEST_DIR.exists():
        print(f"❌ Directory not found: {TEST_DIR}")
        return 1
    
    # Get all image files
    image_files = list(TEST_DIR.glob("*.jpg")) + list(TEST_DIR.glob("*.jpeg")) + \
                  list(TEST_DIR.glob("*.png")) + list(TEST_DIR.glob("*.JPG")) + \
                  list(TEST_DIR.glob("*.JPEG")) + list(TEST_DIR.glob("*.PNG"))
    
    if len(image_files) == 0:
        print(f"❌ No images found in {TEST_DIR}")
        return 1
    
    print(f"Found {len(image_files)} images to rename")
    print()
    
    # Initialize CLIP model
    print("Loading CLIP model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    print(f"✅ CLIP model loaded on {device}")
    print()
    
    # Process each image
    renamed_count = 0
    skipped_count = 0
    
    for idx, img_path in enumerate(tqdm(image_files, desc="Processing images")):
        try:
            # Generate description using CLIP
            description, score = generate_description_with_clip(
                model, preprocess, device, img_path
            )
            
            if description is None:
                skipped_count += 1
                continue
            
            # Generate new filename
            new_filename = generate_filename_from_description(
                description, img_path.name, index=0
            )
            new_path = TEST_DIR / new_filename
            
            # Handle duplicates
            counter = 1
            while new_path.exists() and new_path != img_path:
                new_filename = generate_filename_from_description(
                    description, img_path.name, index=counter
                )
                new_path = TEST_DIR / new_filename
                counter += 1
            
            # Rename if different
            if new_path != img_path:
                img_path.rename(new_path)
                print(f"  {img_path.name[:40]:<40} → {new_filename} (score: {score:.3f})")
                renamed_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            print(f"⚠️  Error processing {img_path.name}: {e}")
            skipped_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Renamed {renamed_count} images")
    print(f"⏭️  Skipped {skipped_count} images")
    print("=" * 60)
    print()
    print("💡 You may want to reindex the photos in the backend after renaming.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

