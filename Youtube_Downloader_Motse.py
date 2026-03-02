import streamlit as st
import yt_dlp
import os
import shutil
import glob

st.set_page_config(page_title="Motse Downloader", page_icon="📥")
st.title("Motse Video Downloader Pro")

# 1. Selection logic
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

if st.button("Prepare Download", use_container_width=True):
    if not url:
        st.error("Missing URL!")
    else:
        tmp_dir = "downloads_tmp"
        if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
            
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        # --- THE FIX FOR 403 FORBIDDEN ---
        ydl_opts = {
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            # This line tells YouTube we are a regular web browser
            'extractor_args': {'youtube': {'player_client': ['web', 'android']}},
        }

        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
        else:
            res = "1080" if quality == "Best" else quality.replace("p","")
            ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'

        if sub_mode == "Timeframe" and not audio_only:
            def s(t):
                p = t.split(':')
                return int(p[0])*3600 + int(p[1])*60 + int(p[2])
            # Newer way to handle ranges to avoid ffmpeg crashes
            ydl_opts['download_ranges'] = lambda info, dict: [{'start_time': s(start_t), 'end_time': s(end_t)}]
            ydl_opts['force_keyframes_at_cuts'] = True

        try:
            with st.spinner("Preparing... YouTube may take a moment to verify the connection."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    for link in urls:
                        if link.strip():
                            ydl.download([link.strip()])
            
            st.success("Download ready!")
            for f in glob.glob(f"{tmp_dir}/*"):
                with open(f, "rb") as b:
                    st.download_button(label=f"💾 Save: {os.path.basename(f)}", data=b, file_name=os.path.basename(f), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: If you get a 403 error, try a different video or wait 5 minutes. YouTube sometimes 'rate limits' cloud servers.")