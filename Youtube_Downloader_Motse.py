import streamlit as st
import yt_dlp
import tkinter as tk
from tkinter import filedialog
import os

# Initialize session state for folder path
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = os.getcwd()

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    root.destroy()
    if folder_selected:
        st.session_state.folder_path = folder_selected

st.title("Motse Video Downloader Pro")

# Section 1: Mode Selection
download_mode = st.radio("Download Mode:", ["Single Video", "Multiple Videos"], horizontal=True)

# Section 2: Input Area
if download_mode == "Single Video":
    url = st.text_input("Paste YouTube URL here:")
    
    # Sub-options for Single Video
    sub_mode = st.radio("Range:", ["All", "Timeframe"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # These are enabled ONLY if "Timeframe" is selected
        start_time = st.text_input("From (HH:MM:SS):", value="00:00:00", disabled=(sub_mode == "All"))
    with col2:
        end_time = st.text_input("To (HH:MM:SS):", value="00:00:10", disabled=(sub_mode == "All"))

else:
    url = st.text_area("Paste Multiple YouTube URLs (one per line):")

# Section 3: Folder Selection
st.write(f"**Current Download Folder:** {st.session_state.folder_path}")
if st.button("Change Folder"):
    select_folder()

# Section 4: Download Logic
if st.button("Start Download"):
    if not url:
        st.error("Please provide a URL!")
    else:
        urls = url.split('\n') if download_mode == "Multiple Videos" else [url]
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{st.session_state.folder_path}/%(title)s.%(ext)s',
            'ffmpeg_location': './ffmpeg.exe', # Assuming ffmpeg is in the app folder
        }

        # Add timeframe logic if selected
        if download_mode == "Single Video" and sub_mode == "Timeframe":
            ydl_opts['download_ranges'] = lambda info, dict: [{
                'start_time': sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(':'))),
                'end_time': sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(':'))),
            }]
            ydl_opts['force_keyframes_at_cuts'] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for link in urls:
                    if link.strip():
                        st.info(f"Downloading: {link}")
                        ydl.download([link.strip()])
            st.success("Finished!")
        except Exception as e:
            st.error(f"Error: {e}")