import streamlit as st
import yt_dlp
import os
import glob

st.title("Motse Video Downloader Pro")

# Section 1: Mode Selection
download_mode = st.radio("Download Mode:", ["Single Video", "Multiple Videos"], horizontal=True)

# Section 2: Input Area
if download_mode == "Single Video":
    url = st.text_input("Paste YouTube URL here:")
    sub_mode = st.radio("Range:", ["All", "Timeframe"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("From (HH:MM:SS):", value="00:00:00", disabled=(sub_mode == "All"))
    with col2:
        end_time = st.text_input("To (HH:MM:SS):", value="00:00:10", disabled=(sub_mode == "All"))
else:
    url = st.text_area("Paste Multiple YouTube URLs (one per line):")

# Section 3: Download Logic
if st.button("Prepare Download"):
    if not url:
        st.error("Please provide a URL!")
    else:
        # Create a downloads folder on the server
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
            
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        if download_mode == "Single Video" and sub_mode == "Timeframe":
            ydl_opts['download_ranges'] = lambda info, dict: [{
                'start_time': sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(':'))),
                'end_time': sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(':'))),
            }]
            ydl_opts['force_keyframes_at_cuts'] = True

        try:
            with st.spinner("Processing..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    for link in urls:
                        if link.strip():
                            ydl.download([link.strip()])
            st.success("Ready for download!")
            
            # Show download buttons for each file found
            files = glob.glob("downloads/*")
            for f in files:
                with open(f, "rb") as file:
                    st.download_button(
                        label=f"Click to Save: {os.path.basename(f)}",
                        data=file,
                        file_name=os.path.basename(f),
                        mime="video/mp4"
                    )
        except Exception as e:
            st.error(f"Error: {e}")