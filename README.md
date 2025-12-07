# AI Photo Search

A web application that uses AI technology to search local photo libraries through natural language queries. The system uses CLIP (Contrastive Language-Image Pre-training) model to understand images and text, enabling semantic search across photos.

## Features

- 🔍 Natural language search queries (e.g., "sunset at the beach", "dogs playing")
- 🖼️ Image gallery with hover effects
- ⚡ Fast semantic search using CLIP embeddings
- 📊 Index statistics and reindexing functionality
- 🎨 Modern, responsive UI
- ⌨️ Enter key support for quick searches

## Why CLIP Model?

CLIP (Contrastive Language-Image Pre-training) is a multimodal AI model developed by OpenAI, particularly suitable for photo search applications:

1. **Multimodal Understanding**: CLIP understands both images and text in the same vector space, enabling direct text-to-image matching without additional text annotations.

2. **Semantic Understanding**: Unlike traditional tag or filename-based search, CLIP understands the actual content and scenes in images.

3. **Zero-shot Learning**: CLIP doesn't require fine-tuning for specific datasets and can directly understand various natural language descriptions.

4. **Efficiency**: ViT-B/32 version maintains good performance with moderate model size (~150MB) and fast inference speed.

5. **Open Source**: CLIP is open source with active community support and comprehensive documentation.

6. **Privacy Protection**: All processing is done locally, protecting user privacy.

## Architecture

- **Backend**: FastAPI with CLIP model for image-text matching
- **Frontend**: Streamlit (recommended) or React
- **AI Model**: OpenAI CLIP (ViT-B/32) for semantic understanding

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ (only if using React frontend)
- Local photo library directory

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set photo library path (optional, defaults to `test_photos/`):
```bash
export PHOTO_LIBRARY_PATH="/path/to/your/photos"
```

5. Start backend server:
```bash
python main.py
```

The backend will:
- Load CLIP model (may take a minute on first run)
- Automatically index all images in the photo library
- Start API server at http://localhost:8000

### Frontend Setup

#### Option 1: Streamlit (Recommended)

Streamlit provides a modern, user-friendly interface with features like click-to-view full-size images and threshold filtering.

1. Install Streamlit (if not already installed):
```bash
pip install streamlit
```

2. Start Streamlit frontend:
```bash
streamlit run frontend_streamlit.py
```

Frontend will be available at http://localhost:8501

#### Option 2: React Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Usage

### Streamlit Frontend (Recommended)

1. Start backend server (in `backend/` directory):
```bash
python main.py
```

2. Start Streamlit frontend (in project root):
```bash
streamlit run frontend_streamlit.py
```

3. Open http://localhost:8501 in your browser

4. **Features**:
   - 🔍 Natural language search
   - 🖼️ Click images to view full size
   - 📊 Similarity score display
   - ⚙️ Threshold filtering: show only images above similarity threshold
   - 📈 Adjustable result count (1-50)
   - ⌨️ Press Enter to search

5. **Search Parameters**:
   - **Result Count**: Control maximum number of images returned
   - **Enable Threshold Filter**: Show only images with similarity scores above threshold
   - **Similarity Threshold**: Set minimum similarity score (0.0-1.0)

### Example Queries

- "sunset on the mountain"
- "smiling people"
- "food on the table"
- "cats and dogs"
- "beach vacation"
- "wedding ceremony"
- "snow scene"
- "woman lying on the beach"
- "man singing"
- "playing cats"

## Downloading Test Images

### Download Flickr30k Dataset

The project includes a script to download images from the Flickr30k dataset for testing:

```bash
python download_flickr30k.py
```

**Options**:
- Default: Downloads up to 10,000 images
- Custom limit: `python download_flickr30k.py --max-images 5000`
- Minimum: `python download_flickr30k.py --max-images 200`

**Download Methods** (tried in order):
1. **Hugging Face** (Fast Streaming) - No credentials needed
2. **Kaggle API** - Requires Kaggle credentials (see below)

**Kaggle Setup** (if Hugging Face fails):
1. Install Kaggle CLI: `pip install kaggle`
2. Get API token from https://www.kaggle.com/account
3. Place `kaggle.json` in `~/.kaggle/`
4. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

**Output**:
- Images are downloaded to `test_photos/` directory
- Old images in `test_photos/` are automatically cleared
- Script shows download progress

**Note**: The script will extract only the specified number of images from the dataset to save time and disk space.

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `GET /stats` - Get indexing statistics
- `POST /search` - Search images
  ```json
  {
    "query": "your search query",
    "limit": 20,
    "threshold": 0.2,
    "use_threshold": false
  }
  ```
- `POST /reindex` - Force reindex all images
- `GET /image` - Serve image files through backend API

## Configuration

### Photo Library Path

By default, the system looks for photos in `test_photos/` directory. You can change this:

1. Set environment variable:
```bash
export PHOTO_LIBRARY_PATH="/path/to/your/photos"
```

2. Or modify `PHOTO_LIBRARY_PATH` variable in `backend/main.py`

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)
- TIFF (.tiff, .tif)

## Performance

- First run will download CLIP model (~150MB)
- Initial indexing may take some time depending on number of images
- Embeddings are cached in `image_embeddings.npy` and `image_paths.json`
- Reindexing is only needed when adding new photos

## Index Files

The system generates two cache files when indexing images:

### `image_embeddings.npy`
- **Type**: NumPy array file (binary format)
- **Content**: CLIP embedding vectors for all images
- **Format**: 2D array with shape `(number_of_images, 512)`
- **Purpose**: Store semantic features for fast similarity computation

### `image_paths.json`
- **Type**: JSON text file
- **Content**: List of full paths to all images
- **Format**: Array of strings, each element is an absolute path
- **Purpose**: Map vector indices back to actual image paths

### How It Works

These files are paired, with array index positions establishing correspondence:

```
Indexing:
Image → CLIP Model → Embedding Vector (512-dim) → Save to image_embeddings.npy[index]
Path → Save to image_paths.json[index]

Searching:
Query Text → CLIP Model → Query Vector (512-dim)
Query Vector vs All Image Vectors → Compute Similarity → Find Best Matching Indices
Indices → Get Paths from image_paths.json[index] → Return Results
```

### File Location

These files are saved in the `backend/` directory by default and are excluded from version control via `.gitignore`.

## Troubleshooting

### Images Not Loading

If images fail to load:
1. Check browser console for errors
2. Verify backend server is running
3. Check image paths are correct

### Model Loading Issues

If CLIP model fails to load:
- Ensure sufficient disk space (model ~338MB)
- Check network connection (for first-time download)
- Verify PyTorch installation

**CLIP Model Cache Location**:
- Default: `~/.cache/clip/`
- Model file: `~/.cache/clip/ViT-B-32.pt` (~338MB)
- Only downloaded once on first use

### Indexing Fails

- Verify photo library path exists
- Check file permissions
- Ensure images are in supported formats

### Proxy Issues

If encountering SOCKS proxy errors:
- Temporarily disable proxy: `unset ALL_PROXY && pip install ...`
- Or use mirror: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ...`

## Project Structure

```
cursor-photo-search/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API server
│   ├── requirements.txt # Python dependencies
│   └── venv/            # Virtual environment
├── frontend_streamlit.py # Streamlit frontend
├── download_flickr30k.py # Script to download test images
├── test_photos/          # Test images directory (gitignored)
└── README.md            # This file
```

## License

MIT
