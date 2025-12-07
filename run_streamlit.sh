#!/bin/bash
# Run Streamlit frontend
cd "$(dirname "$0")"
streamlit run frontend_streamlit.py --server.port 8501
