import streamlit as st
import yt_dlp
import os
import wave
import contextlib
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from gtts import gTTS
import ffmpeg

# Streamlit App Title
st.title("YouTube Video Language Translator")
st.write("Translate YouTube video audio to your desired language.")

# Input: YouTube Link
youtube_url = st.text_input("Enter YouTube video URL:")

# Expanded List of Output Languages
output_language = st.selectbox(
    "Select the target language:",
    [
        "en", "te", "es", "fr", "de", "hi", "zh", "ar", "ja", "ko", "ru", "it", "pt", "tr", "pl", "nl", "sv", "da", "fi", "cs", "el", "vi", "th", "uk", "hu",
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

# Helper function to get audio duration
def get_audio_duration(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

# Helper function to transcribe audio
def transcribe_audio(audio_path, model):
    segments, _ = model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments)

# Helper function for text-to-speech conversion
def text_to_speech(translated_text, output_audio_file, language='en'):
    tts = gTTS(text=translated_text, lang=language)
    tts.save(output_audio_file)

# Helper function to replace audio in video
def replace_audio_in_video(video_file, audio_file, output_file):
    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.output(input_video, input_audio, output_file, vcodec='copy', acodec='aac').run()

# Process Button
if st.button("Translate"):
    if youtube_url:
        try:
            # Download YouTube video audio
            st.write("Downloading audio from video...")
            audio_path = "audio.mp3"
            download_audio(youtube_url, audio_path)

            # Convert MP3 to WAV
            st.write("Converting audio format...")
            audio = AudioSegment.from_mp3(audio_path)
            wav_path = "audio.wav"
            audio.export(wav_path, format="wav")

            # Transcribe audio using Faster Whisper
            st.write("Transcribing audio...")
            whisper_model = WhisperModel("base")
            transcription = transcribe_audio(wav_path, whisper_model)

            # Translate transcription using GoogleTranslator
            st.write("Translating transcription...")
            translated_text = GoogleTranslator(source='auto', target=output_language).translate(transcription)

            # Generate translated audio from text
            st.write("Generating translated audio...")
            translated_audio_file = "translated_audio.mp3"
            text_to_speech(translated_text, translated_audio_file, language=output_language)

            # Replace audio in video
            st.write("Replacing audio in video...")
            video_file = "video.mp4"  # Placeholder video file name
            output_video_file = "output_video.mp4"
            replace_audio_in_video(video_file, translated_audio_file, output_video_file)

            # Clean up temporary files
            os.remove(wav_path)
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
