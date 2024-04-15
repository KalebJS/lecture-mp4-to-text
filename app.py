import os
from pathlib import Path

import streamlit as st
import whisper
from moviepy.editor import VideoFileClip

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


model_size = st.sidebar.selectbox(
    "Model Size", ["large", "medium", "small", "base", "tiny"], index=2
)
language = st.sidebar.radio("Model Language", ["English", "Multilingual"])

# Set the model path based on the selected options
if language == "English":
    model_path = f"{model_size}.en"
else:
    model_path = model_size

# Upload video file
uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "m4a"])

run_button = st.button("Transcribe")

if not run_button:
    st.stop()

if uploaded_file is None:
    st.error("Must upload mp4 or m4a file.")
    st.stop()

# Save the uploaded file to a temporary location
with open(TEMP_DIR / uploaded_file.name, "wb") as file:
    file.write(uploaded_file.getbuffer())

# Set the file path and extension
filepath = TEMP_DIR / uploaded_file.name
file_extension = os.path.splitext(filepath)[1]

# Extract audio from video
if file_extension.lower() == ".mp4":
    # Convert MP4/M4A to WAV
    audio_path = filepath.with_suffix(".wav")
    video_clip = VideoFileClip(str(filepath))
    audio_clip = video_clip.audio
    if audio_clip is None:
        raise ValueError("The video does not contain any audio.")
    audio_clip.write_audiofile(audio_path)
elif file_extension.lower() == ".m4a":
    audio_path = filepath
else:
    raise ValueError("The file extension is not supported.")

# Load the Whisper model
model = whisper.load_model(model_path)

st.success("MP4/M4A file converted to WAV successfully.")

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
        label="Download Transcript as TXT",
        data=file,
        file_name="transcript.txt",
        mime="text/plain",
    )
