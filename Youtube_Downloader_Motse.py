import streamlit as st
import yt_dlp
import os
import shutil
import glob

st.set_page_config(page_title="Motse Downloader", page_icon="📥")
st.title("Motse Video Downloader Pro")

# 1. Layout & Options
download_mode = st.radio("Download Mode:", ["Single Video", "Multiple Videos"], horizontal=True)
col_a, col_q = st.columns(2)
with col_a:
    audio_only = st.checkbox("🎵 Audio Only (MP3)")
with col_q:
    quality = st.selectbox("Quality:", ["Best", "1080p", "720p", "480p"], disabled=audio_only)

if download_mode == "Single Video":
    url = st.text_input("Paste URL here:")
    sub_mode = st.radio("Range:", ["All", "Timeframe"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        start_t = st.text_input("From (HH:MM:SS):", value="00:00:00", disabled=(sub_mode == "All"))
    with c2:
        end_t = st.text_input("To (HH:MM:SS):", value="00:00:10", disabled=(sub_mode == "All"))
else:
    url = st.text_area("Paste URLs (one per line):")

# 2. The Download Engine
if st.button("Prepare Download", use_container_width=True):
    if not url:
        st.error("Missing URL!")
    else:
        tmp_dir = "downloads_tmp"
        if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
            
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        # --- THE 2026 FIX FOR 403 FORBIDDEN ---
        ydl_opts = {
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
            # Workaround for YouTube