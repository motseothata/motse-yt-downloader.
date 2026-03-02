import streamlit as st
import yt_dlp
import os
import shutil
import glob

st.set_page_config(page_title="Motse Downloader", page_icon="📥")
st.title("Motse Video Downloader Pro")

# 1. Selection logic
download_mode = st.radio("Download Mode:", ["Single Video", "Multiple Videos"], horizontal=True)

# Audio & Quality Options
col_a, col_q = st.columns(2)
with col_a:
    audio_only = st.checkbox("🎵 Audio Only (MP3)")
with col_q:
    quality = st.selectbox(
        "Video Quality:",
        ["Best Available", "1080p", "720p", "480p", "360p"],
        disabled=audio_only
    )

if download_mode == "Single Video":
    url = st.text_input("Paste URL here:")
    sub_mode = st.radio("Range:", ["All", "Timeframe"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("From (HH:MM:SS):", value="00:00:00", disabled=(sub_mode == "All" or audio_only))
    with col2:
        end_time = st.text_input("To (HH:MM:SS):", value="00:00:10", disabled=(sub_mode == "All" or audio_only))
else:
    url = st.text_area("Paste URLs (one per line):")

if st.button("Prepare Download", use_container_width=True):
    if not url:
        st.error("Please provide a URL!")
    else:
        tmp_dir = "downloads_tmp"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
            
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        # Base Options
        ydl_opts = {
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
        }

        # 2. Handle Quality and Audio Logic
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Map user choice to yt-dlp format strings
            if quality == "Best Available":
                # Forces MP4 container for best phone compatibility
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                res = quality.replace("p", "")
                # Selects best video UP TO the chosen height, merged into MP4
                ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'

        # 3. Timeframe Logic
        if not audio_only and download_mode == "Single Video" and sub_mode == "Timeframe":
            def to_secs(t_str):
                p = t_str.split(':')
                return int(p[0])*3600 + int(p[1])*60 + int(p[2])
            ydl_opts['download_ranges'] = lambda info, dict: [{
                'start_time': to_secs(start_time),
                'end_time': to_secs(end_time),
            }]
            ydl_opts['force_keyframes_at_cuts'] = True

        try:
            with st.spinner(f"Processing {quality if not audio_only else 'Audio'}..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    for link in urls:
                        if link.strip():
                            ydl.download([link.strip()])
            
            st.success("Download ready!")
            files = glob.glob(f"{tmp_dir}/*")
            for f in files:
                with open(f, "rb") as file_bytes:
                    st.download_button(
                        label=f"💾 Save: {os.path.basename(f)}",
                        data=file_bytes,
                        file_name=os.path.basename(f),
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Error: {e}")