import streamlit as st
import yt_dlp
import os
import shutil
import glob

# Page setup for mobile friendliness
st.set_page_config(page_title="Motse Downloader", page_icon="📥", layout="centered")
st.title("Motse Video Downloader Pro")

# 1. Selection logic
download_mode = st.radio("Download Mode:", ["Single Video", "Multiple Videos"], horizontal=True)

if download_mode == "Single Video":
    url = st.text_input("Paste YouTube URL here:")
    sub_mode = st.radio("Range:", ["All", "Timeframe"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("From (HH:MM:SS):", value="00:00:00", disabled=(sub_mode == "All"))
    with col2:
        end_time = st.text_input("To (HH:MM:SS):", value="00:00:10", disabled=(sub_mode == "All"))
else:
    url = st.text_area("Paste URLs (one per line):")

# 2. Preparation Logic
if st.button("Prepare Download", use_container_width=True):
    if not url:
        st.error("Please provide a URL!")
    else:
        # Create/Clear temp directory
        tmp_dir = "downloads_tmp"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
            
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        # Options optimized for Cloud
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True if download_mode == "Single Video" else False,
        }

        # Add timeframe logic if needed
        if download_mode == "Single Video" and sub_mode == "Timeframe":
            # Convert HH:MM:SS to seconds
            def to_secs(t_str):
                parts = t_str.split(':')
                return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            
            ydl_opts['download_ranges'] = lambda info, dict: [{
                'start_time': to_secs(start_time),
                'end_time': to_secs(end_time),
            }]
            ydl_opts['force_keyframes_at_cuts'] = True

        try:
            with st.spinner("Processing on server..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    for link in urls:
                        if link.strip():
                            ydl.download([link.strip()])
            
            st.success("Ready! Save the file below:")
            
            # 3. Create Download Buttons for each file
            files = glob.glob(f"{tmp_dir}/*")
            for f in files:
                with open(f, "rb") as file_bytes:
                    st.download_button(
                        label=f"💾 Save: {os.path.basename(f)}",
                        data=file_bytes,
                        file_name=os.path.basename(f),
                        mime="video/mp4",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Download Error: {e}")