import os

import streamlit as st
import whisper
from moviepy.editor import VideoFileClip
from pathlib import Path


TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


st.title("MP4 to transcript converter")
uploaded_file = st.file_uploader("Choose an MP4 file", type="mp4", )
filepath = None
if uploaded_file is not None:
    # Save the file to the server
    filepath = TEMP_DIR / uploaded_file.name
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded successfully.")
else:
    st.error("Please upload an MP4 file.")
    st.stop()
# Check if the uploaded file extension is mp4
file_extension = filepath.suffix
if file_extension.lower() != ".mp4":
    st.error("The file you uploaded is not an MP4 file. Please upload an MP4 file.")
    st.stop()

# Load the Whisper model
model = whisper.load_model("base")

# Convert MP4 to WAV
audio_path = filepath.with_suffix(".wav")

# Extract audio from video
video_clip = VideoFileClip(str(filepath))
audio_clip = video_clip.audio
if audio_clip is None:
    raise ValueError("The video does not contain any audio.")
audio_clip.write_audiofile(audio_path)

st.success("MP4 file converted to WAV successfully.")

result = model.transcribe(str(audio_path), verbose=True)
transcript = result["text"]
if not isinstance(transcript, str):
    raise ValueError("The transcript is not a string.")
st.text_area("Transcript", transcript, height=300)
# Give the user the option to download the transcript as a .txt file
transcript_file_path = TEMP_DIR / "transcript.txt"
with open(transcript_file_path, "w") as text_file:
    text_file.write(transcript)

with open(transcript_file_path, "rb") as file:
    btn = st.download_button(
        label="Download Transcript as TXT", data=file, file_name="transcript.txt", mime="text/plain"
    )
