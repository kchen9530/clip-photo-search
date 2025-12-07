import streamlit as st
import requests
import os
from pathlib import Path
from PIL import Image
import io

# Disable proxy for requests to avoid SOCKS connection issues
os.environ.pop('ALL_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# Page configuration
st.set_page_config(
    page_title="AI 照片搜索",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .image-card {
        border-radius: 10px;
        padding: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .score-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    /* Make image clickable */
    div[data-testid="stImage"] {
        cursor: pointer;
        position: relative;
    }
    /* Hide button text and make it overlay the image */
    button[data-testid="baseButton-secondary"]:empty,
    button[data-testid="baseButton-secondary"]:has-text("") {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent;
        border: none;
        cursor: pointer;
        z-index: 1;
        opacity: 0;
        padding: 0;
        margin: 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a91 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def get_stats():
    """Get indexing statistics from backend"""
    try:
        # Disable proxy for local connections
        response = requests.get(
            f"{API_BASE}/stats", 
            timeout=10,
            proxies={'http': None, 'https': None}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        return None

def search_images(query, limit, threshold, use_threshold):
    """Search for images"""
    try:
        payload = {
            "query": query,
            "limit": limit,
            "threshold": threshold,
            "use_threshold": use_threshold
        }
        response = requests.post(
            f"{API_BASE}/search",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"},
            proxies={'http': None, 'https': None}  # Disable proxy for local connections
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"搜索失败 (状态码: {response.status_code}): {response.text[:200]}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到后端服务器。请确保后端正在运行 (http://localhost:8000)")
        return []
    except requests.exceptions.Timeout:
        st.error("⏱️ 请求超时。请稍后重试。")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 网络错误: {str(e)[:200]}")
        return []
    except Exception as e:
        st.error(f"❌ 搜索错误: {str(e)[:200]}")
        return []

def get_image_url(image_path):
    """Get image URL from backend"""
    encoded_path = requests.utils.quote(image_path, safe='')
    return f"{API_BASE}/image?path={encoded_path}"

# Header
st.markdown('<h1 class="main-header">🔍 AI 照片搜索</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">使用自然语言搜索你的照片库</p>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ 设置")
    
    # Backend connection status
    st.subheader("🔌 连接状态")
    try:
        health_response = requests.get(
            f"{API_BASE}/health", 
            timeout=5,
            proxies={'http': None, 'https': None}  # Disable proxy for local connections
        )
        if health_response.status_code == 200:
            st.success("✅ 后端已连接")
        else:
            st.error(f"❌ 后端响应异常 (状态码: {health_response.status_code})")
            st.info("请检查后端服务器状态")
    except requests.exceptions.ConnectionError:
        st.error("❌ 后端未连接")
        st.info("请确保后端正在运行：\n```bash\ncd backend\npython main.py\n```")
    except requests.exceptions.Timeout:
        st.warning("⏱️ 连接超时，请稍后重试")
    except Exception as e:
        st.error(f"❌ 连接错误: {str(e)[:50]}")
        st.info("请检查后端服务器是否正常运行")
    
    st.divider()
    
    # Stats
    st.subheader("📊 索引统计")
    stats = get_stats()
    if stats:
        if stats.get("indexed"):
            st.success(f"✅ 已索引: {stats.get('total_images', 0)} 张图片")
            st.info(f"📁 路径: {stats.get('photo_library_path', 'N/A')}")
        else:
            st.warning("⚠️ 尚未索引图片")
    else:
        st.warning("⚠️ 无法获取索引统计")
    
    st.divider()
    
    # Search parameters
    st.subheader("🔍 搜索参数")
    limit = st.slider("返回结果数量", min_value=1, max_value=50, value=10, step=1)
    
    use_threshold = st.checkbox("启用阈值过滤", value=False, help="只显示相似度分数高于阈值的图片")
    
    threshold = st.slider(
        "相似度阈值",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        disabled=not use_threshold,
        help="相似度分数低于此值的图片将被过滤"
    )
    
    st.divider()
    
    # Reindex button
    if st.button("🔄 重新索引", use_container_width=True):
        with st.spinner("正在重新索引..."):
            try:
                response = requests.post(
                    f"{API_BASE}/reindex", 
                    timeout=300,
                    proxies={'http': None, 'https': None}  # Disable proxy for local connections
                )
                if response.status_code == 200:
                    st.success("重新索引完成！")
                    st.rerun()
                else:
                    st.error("重新索引失败")
            except Exception as e:
                st.error(f"重新索引错误: {e}")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "搜索查询",
        placeholder="例如：'女人躺在海滩上'、'猫在玩耍'、'火车票'",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔍 搜索", use_container_width=True)

# Search and display results
if search_button and search_query:
    with st.spinner("正在搜索..."):
        results = search_images(search_query, limit, threshold, use_threshold)
        st.session_state.search_results = results
        st.session_state.selected_image = None  # Clear selected image on new search

# Display results in a clean list format
if st.session_state.search_results:
    st.divider()
    st.subheader(f"📸 找到 {len(st.session_state.search_results)} 张相关图片")
    
    # Display results as a list
    for idx, result in enumerate(st.session_state.search_results):
        image_url = get_image_url(result['path'])
        score = result['score']
        score_percent = score * 100
        file_name = Path(result['path']).name
        
        # Create a container for each result item
        with st.container():
            # Use columns for layout: thumbnail on left, info on right
            col_img, col_info = st.columns([2, 3])
            
            with col_img:
                # Display thumbnail image
                try:
                    img_response = requests.get(
                        image_url, 
                        timeout=15,
                        proxies={'http': None, 'https': None}
                    )
                    if img_response.status_code == 200:
                        img = Image.open(io.BytesIO(img_response.content))
                        
                        # Display thumbnail - click to view full size
                        st.image(img, use_container_width=True)
                        
                        # Clickable button overlay
                        if st.button("🔍 查看大图", key=f"view_{idx}", use_container_width=True):
                            st.session_state.selected_image = {
                                'path': result['path'],
                                'score': score,
                                'url': image_url
                            }
                            st.rerun()
                    else:
                        st.error(f"图片加载失败 (状态码: {img_response.status_code})")
                        st.text(f"URL: {image_url}")
                        st.text(f"路径: {result['path']}")
                except requests.exceptions.RequestException as e:
                    st.error(f"图片加载失败: {str(e)[:100]}")
                    st.text(f"URL: {image_url}")
                except Exception as e:
                    st.error(f"图片错误: {str(e)[:100]}")
                    st.text(f"路径: {result['path']}")
            
            with col_info:
                # File information
                st.markdown(f"### {file_name}")
                
                # Similarity score with progress bar
                st.markdown(f"**相似度**: {score_percent:.1f}%")
                st.progress(score, text="")
                
                # File path (collapsible)
                with st.expander("📁 查看完整路径"):
                    st.code(result['path'], language=None)
                
                # Additional info
                st.caption(f"结果 #{idx + 1} / {len(st.session_state.search_results)}")
            
            # Divider between items
            if idx < len(st.session_state.search_results) - 1:
                st.divider()

# Full size image modal - display at top of page
if st.session_state.selected_image:
    selected = st.session_state.selected_image
    
    st.divider()
    st.subheader("🖼️ 大图预览")
    
    try:
        img_response = requests.get(
            selected['url'], 
            timeout=15,
            proxies={'http': None, 'https': None}  # Disable proxy for local connections
        )
        if img_response.status_code == 200:
            img = Image.open(io.BytesIO(img_response.content))
            
            # Display image in large size
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.image(img, use_container_width=True)
                
                # Image info
                st.info(f"**路径**: {selected['path']}  \n**相似度**: {selected['score']*100:.2f}%")
                
                # Close button
                if st.button("❌ 关闭大图", key="close_fullscreen", use_container_width=True):
                    st.session_state.selected_image = None
                    st.rerun()
        else:
            st.error(f"无法加载大图 (状态码: {img_response.status_code})")
            if st.button("❌ 关闭", key="close_error", use_container_width=True):
                st.session_state.selected_image = None
                st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"大图加载失败: {str(e)[:100]}")
        if st.button("❌ 关闭", key="close_request_error", use_container_width=True):
            st.session_state.selected_image = None
            st.rerun()
    except Exception as e:
        st.error(f"大图处理错误: {str(e)[:100]}")
        if st.button("❌ 关闭", key="close_exception", use_container_width=True):
            st.session_state.selected_image = None
            st.rerun()
    
    st.divider()

# Example queries
if not st.session_state.search_results:
    st.divider()
    st.subheader("💡 示例查询")
    
    example_queries = [
        "女人躺在海滩上",
        "男人在唱歌",
        "猫在玩耍",
        "狗在海滩",
        "火车票",
        "身份证",
        "信用卡",
        "海滩日落",
        "人们在餐厅",
        "办公室会议"
    ]
    
    cols = st.columns(5)
    for idx, query in enumerate(example_queries):
        with cols[idx % 5]:
            if st.button(query, key=f"example_{idx}", use_container_width=True):
                # Directly trigger search with example query
                with st.spinner("正在搜索..."):
                    results = search_images(query, limit, threshold, use_threshold)
                    st.session_state.search_results = results
                    st.session_state.selected_image = None
                    st.rerun()

# Footer
st.divider()
st.markdown(
    '<p style="text-align: center; color: #999; font-size: 0.9rem;">Powered by CLIP & FastAPI • 本地隐私保护</p>',
    unsafe_allow_html=True
)

