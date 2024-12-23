
import streamlit as st
from moviepy.editor import AudioFileClip, VideoFileClip
import whisper
from libretranslatepy import LibreTranslateAPI
import srt
import yt_dlp
import os
from gtts import gTTS

# Streamlit App Title
st.title("YouTube Video Language Translator")
st.write("Paste a YouTube link to translate the video audio to your desired language.")

# Input: YouTube Link
youtube_url = st.text_input("Enter YouTube video URL:")

# Expanded List of Output Languages
output_language = st.selectbox(
    "Select the target language:",
    [
        "en",  # English
        "te",  # Telugu
        "es",  # Spanish
        "fr",  # French
        "de",  # German
        "hi",  # Hindi
        "zh",  # Chinese (Simplified)
        "ar",  # Arabic
        "ja",  # Japanese
        "ko",  # Korean
        "ru",  # Russian
        "it",  # Italian
        "pt",  # Portuguese
        "tr",  # Turkish
        "pl",  # Polish
        "nl",  # Dutch
        "sv",  # Swedish
        "da",  # Danish
        "fi",  # Finnish
        "cs",  # Czech
        "el",  # Greek
        "vi",  # Vietnamese
        "th",  # Thai
        "uk",  # Ukrainian
        "hu",  # Hungarian
    ]
)

# Helper function to download audio using yt-dlp
def download_audio(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

# Helper function for text-to-speech conversion
def text_to_speech(translated_text, output_audio_file, language='en'):
    tts = gTTS(text=translated_text, lang=language)
    tts.save(output_audio_file)

# Helper function to replace audio in video
def replace_audio_in_video(video_file, audio_file, output_file):
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    video = video.set_audio(audio)
    video.write_videofile(output_file, codec='libx264')

# Process Button
if st.button("Translate"):
    if youtube_url:
        try:
            # Download YouTube video audio
            st.write("Downloading audio from video...")
            audio_path = "audio.mp3"
            download_audio(youtube_url, audio_path)

            # Extract audio as wav format
            st.write("Extracting audio...")
            audio_clip = AudioFileClip(audio_path)
            audio_file = "audio.wav"
            audio_clip.write_audiofile(audio_file)

            # Transcribe audio using Whisper
            st.write("Transcribing audio...")
            model = whisper.load_model("base")
            transcription = model.transcribe(audio_file)["text"]

            # Translate transcription using LibreTranslate
            st.write("Translating transcription...")
            translator = LibreTranslateAPI()
            translated_text = translator.translate(
                transcription, source="en", target=output_language
            )

            # Generate translated audio from text
            st.write("Generating translated audio...")
            translated_audio_file = "translated_audio.mp3"
            text_to_speech(translated_text, translated_audio_file, language=output_language)

            # Replace audio in video
            st.write("Replacing audio in video...")
            video_file = "video.mp4"  # Assuming the video file is available
            output_video_file = "output_video.mp4"
            replace_audio_in_video(video_file, translated_audio_file, output_video_file)

            # Clean up temporary files
            os.remove(audio_file)
            os.remove(audio_path)
            os.remove(translated_audio_file)

            # Provide download links for the final video
            st.success("Translation completed!")
            st.download_button(
                label="Download Translated Video",
                data=open(output_video_file, "rb"),
                file_name="translated_video.mp4",
                mime="video/mp4"
            )

        except yt_dlp.utils.DownloadError:
            st.error("Failed to download video. Please check the URL or try again later.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid YouTube URL.")
