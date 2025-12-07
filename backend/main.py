from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import clip
import urllib.parse

app = FastAPI(title="Photo Search API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
clip_model = None
clip_preprocess = None
device = None

# Configuration
# Default to test_photos directory for Flickr30k dataset
# Can be overridden with PHOTO_LIBRARY_PATH environment variable
DEFAULT_PHOTO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_photos")
PHOTO_LIBRARY_PATH = os.getenv("PHOTO_LIBRARY_PATH", DEFAULT_PHOTO_PATH)
INDEX_FILE = "image_index.json"
EMBEDDINGS_FILE = "image_embeddings.npy"
IMAGE_PATHS_FILE = "image_paths.json"

class SearchRequest(BaseModel):
    query: str
    limit: int = 20
    threshold: float = 0.0  # Minimum similarity score threshold
    use_threshold: bool = False  # Whether to use threshold filtering

class SearchResult(BaseModel):
    path: str
    score: float

def initialize_models():
    """Initialize CLIP model for image-text matching"""
    global clip_model, clip_preprocess, device
    
    if clip_model is None:
        print("Loading CLIP model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        clip_model.eval()
        print(f"CLIP model loaded on {device}")

def get_image_files(directory: str) -> List[str]:
    """Recursively get all image files from directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    image_files = []
    
    directory_path = Path(directory)
    if not directory_path.exists():
        return image_files
    
    for ext in image_extensions:
        image_files.extend(directory_path.rglob(f"*{ext}"))
        image_files.extend(directory_path.rglob(f"*{ext.upper()}"))
    
    return [str(f) for f in image_files]

def compute_image_embedding(image_path: str) -> Optional[np.ndarray]:
    """Compute CLIP embedding for an image"""
    try:
        image = Image.open(image_path).convert('RGB')
        image_tensor = clip_preprocess(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            image_features = clip_model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy().flatten()
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def index_images(force_reindex: bool = False, check_new_images: bool = False):
    """Index all images in the photo library"""
    print(f"Indexing images from: {PHOTO_LIBRARY_PATH}")
    
    # If force reindex, clear old index files first
    if force_reindex:
        print("Force reindex: Clearing old index files...")
        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)
        if os.path.exists(EMBEDDINGS_FILE):
            os.remove(EMBEDDINGS_FILE)
        if os.path.exists(IMAGE_PATHS_FILE):
            os.remove(IMAGE_PATHS_FILE)
    
    # Check if index exists and is valid
    if not force_reindex and os.path.exists(INDEX_FILE) and os.path.exists(EMBEDDINGS_FILE):
        if check_new_images:
            # Check if there are new images
            current_images = set(get_image_files(PHOTO_LIBRARY_PATH))
            with open(IMAGE_PATHS_FILE, 'r') as f:
                indexed_paths = set(json.load(f))
            
            # Verify indexed paths still exist
            valid_indexed_paths = {p for p in indexed_paths if os.path.exists(p)}
            removed_images = indexed_paths - valid_indexed_paths
            new_images = current_images - indexed_paths
            
            if new_images or removed_images:
                print(f"Detected changes: {len(new_images)} new images, {len(removed_images)} removed")
                print("Reindexing to update index...")
                force_reindex = True
            else:
                print("Using existing index (no changes detected)")
                return
        else:
            print("Using existing index")
            return
    
    # Get all image files
    image_files = get_image_files(PHOTO_LIBRARY_PATH)
    print(f"Found {len(image_files)} images")
    
    if len(image_files) == 0:
        print("No images found!")
        return
    
    # Compute embeddings - only for files that actually exist
    embeddings = []
    valid_paths = []
    
    for i, img_path in enumerate(image_files):
        # Verify file exists before processing
        if not os.path.exists(img_path):
            print(f"⚠️  Skipping non-existent file: {img_path}")
            continue
            
        if i % 10 == 0:
            print(f"Processing {i+1}/{len(image_files)}...")
        
        embedding = compute_image_embedding(img_path)
        if embedding is not None:
            embeddings.append(embedding)
            valid_paths.append(img_path)
    
    if len(embeddings) == 0:
        print("No valid embeddings generated!")
        return
    
    # Save embeddings and paths
    embeddings_array = np.array(embeddings)
    np.save(EMBEDDINGS_FILE, embeddings_array)
    
    with open(IMAGE_PATHS_FILE, 'w') as f:
        json.dump(valid_paths, f)
    
    # Create index metadata
    index_data = {
        "total_images": len(valid_paths),
        "photo_library_path": PHOTO_LIBRARY_PATH,
        "embedding_dim": embeddings_array.shape[1]
    }
    
    with open(INDEX_FILE, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"Indexed {len(valid_paths)} images successfully!")

@app.on_event("startup")
async def startup_event():
    """Initialize models and index on startup"""
    initialize_models()
    # Force reindex on startup to pick up new Flickr30k photos
    # This ensures we always use the latest photos and ignore old ones
    print("Starting up: Reindexing photos to ensure latest dataset is indexed...")
    index_images(force_reindex=True)

@app.get("/")
async def root():
    return {"message": "Photo Search API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/search", response_model=List[SearchResult])
async def search_images(request: SearchRequest):
    """Search for images matching the query"""
    if clip_model is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    # Load embeddings and paths
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(IMAGE_PATHS_FILE):
        raise HTTPException(status_code=404, detail="Image index not found. Please index images first.")
    
    embeddings = np.load(EMBEDDINGS_FILE)
    with open(IMAGE_PATHS_FILE, 'r') as f:
        image_paths = json.load(f)
    
    # Verify that embeddings and paths match
    if len(embeddings) != len(image_paths):
        raise HTTPException(status_code=500, detail="Index mismatch: embeddings and paths count don't match. Please reindex.")
    
    # Filter out non-existent files and their corresponding embeddings
    valid_indices = []
    valid_embeddings = []
    valid_paths = []
    
    for idx, img_path in enumerate(image_paths):
        if os.path.exists(img_path):
            valid_indices.append(idx)
            valid_embeddings.append(embeddings[idx])
            valid_paths.append(img_path)
    
    if len(valid_embeddings) == 0:
        raise HTTPException(status_code=404, detail="No valid images found in index. Please reindex.")
    
    if len(valid_embeddings) < len(embeddings):
        print(f"⚠️  Warning: {len(embeddings) - len(valid_embeddings)} indexed images no longer exist. Consider reindexing.")
        # Update embeddings array
        valid_embeddings = np.array(valid_embeddings)
    
    # Encode query text
    with torch.no_grad():
        text_tokens = clip.tokenize([request.query]).to(device)
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        query_embedding = text_features.cpu().numpy().flatten()
    
    # Compute similarity scores
    similarities = np.dot(valid_embeddings, query_embedding)
    
    # Get top results
    top_indices = np.argsort(similarities)[::-1][:request.limit]
    
    # Filter by threshold if enabled
    if request.use_threshold:
        filtered_indices = [idx for idx in top_indices if similarities[idx] >= request.threshold]
        if len(filtered_indices) == 0:
            # If no results meet threshold, return top result anyway
            filtered_indices = top_indices[:1] if len(top_indices) > 0 else []
        top_indices = filtered_indices
    
    results = [
        SearchResult(path=valid_paths[idx], score=float(similarities[idx]))
        for idx in top_indices
    ]
    
    return results

@app.post("/reindex")
async def reindex_images():
    """Force reindex all images"""
    index_images(force_reindex=True)
    return {"message": "Reindexing completed", "status": "success"}

@app.get("/stats")
async def get_stats():
    """Get indexing statistics"""
    if not os.path.exists(INDEX_FILE):
        return {"indexed": False, "total_images": 0}
    
    with open(INDEX_FILE, 'r') as f:
        index_data = json.load(f)
    
    return {
        "indexed": True,
        "total_images": index_data.get("total_images", 0),
        "photo_library_path": index_data.get("photo_library_path", PHOTO_LIBRARY_PATH)
    }

@app.get("/image")
async def serve_image(path: str):
    """Serve an image file from the photo library"""
    try:
        # Decode the path if it's URL encoded
        decoded_path = urllib.parse.unquote(path)
        
        # Get the actual photo library path from index if available
        photo_lib_path = Path(PHOTO_LIBRARY_PATH).resolve()
        if os.path.exists(IMAGE_PATHS_FILE):
            try:
                with open(IMAGE_PATHS_FILE, 'r') as f:
                    image_paths = json.load(f)
                    if image_paths and len(image_paths) > 0:
                        # Use the directory of the first indexed image as the photo library path
                        first_image_path = Path(image_paths[0])
                        photo_lib_path = first_image_path.parent.resolve()
            except:
                pass
        
        # Security check: ensure the path is within the photo library
        image_path = Path(decoded_path).resolve()
        
        # Check if path is within photo library or its parent directories
        # This allows for test_photos directory
        if not str(image_path).startswith(str(photo_lib_path)) and not str(photo_lib_path) in str(image_path):
            # Also check if it's in the project directory (for test_photos)
            project_root = Path(__file__).parent.parent.resolve()
            if not str(image_path).startswith(str(project_root)):
                raise HTTPException(status_code=403, detail=f"Access denied. Path: {image_path}, Library: {photo_lib_path}")
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")
        
        return FileResponse(image_path, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

