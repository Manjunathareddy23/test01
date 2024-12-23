import streamlit as st
import yt_dlp
import os
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS

# Streamlit App Title
st.title("YouTube Video Language Translator")
st.write("Translate YouTube video audio to your desired language.")

# Input: YouTube Link
youtube_url = st.text_input("Enter YouTube video URL:")

output_language = st.selectbox(
    "Select your language:",
    [
   
        "en", "te", "es", "fr", "de", "hi", "zh", "ar", "ja", "ko", "ru", "it", "pt", "tr", "pl", "nl", "sv", "da", "fi", "cs", "el", "vi", "th", "uk", "hu",
        "ml", "mr", "bn", "gu", "ta", "kn", "or", "pa", "as", "ne", "si",  # Added Indian languages
        "af", "sq", "hy", "bn", "bs", "ca", "hr", "cs", "da", "nl", "en", "eo", "tl", "et", "fi", "fr", "de", "el", "gu", "hi", "hu", "is", "id", "it", "ja", "jw", 
        "km", "ko", "la", "lv", "lt", "mk", "ml", "mr", "my", "ne", "pl", "ps", "pt", "pa", "ro", "ru", "sr", "si", "sk", "sl", "es", "su", "sw", "sv", "ta", "te", 
        "th", "tr", "uk", "ur", "vi", "cy", "xh", "zu"
    
         
    ]
)
st.write("Language Symbols:")
st.write("English (en)", "Spanish (es)", "French (fr)", "German (de)", "Italian (it)", 
    "Portuguese (pt)", "Russian (ru)", "Dutch (nl)", "Swedish (sv)", "Danish (da)", 
    "Finnish (fi)", "Czech (cs)", "Greek (el)", "Polish (pl)", "Hungarian (hu)", "Hindi (hi)", "Bengali (bn)", "Mandarin Chinese (zh)", "Japanese (ja)", "Korean (ko)", 
    "Arabic (ar)", "Tamil (ta)", "Telugu (te)", "Thai (th)", "Vietnamese (vi)", "Malayalam (ml)", "Marathi (mr)", "Gujarati (gu)", "Kannada (kn)", "Punjabi (pa)", 
    "Oriya (or)", "Assamese (as)", "Nepali (ne)", "Sinhalese (si)", "Swahili (sw)", "Zulu (zu)","Afrikaans (af)", "Albanian (sq)", "Armenian (hy)", "Basque (eu)", "Catalan (ca)", 
    "Bosnian (bs)", "Esperanto (eo)", "Filipino (tl)", "Estonian (et)", "Icelandic (is)", 
    "Indonesian (id)", "Javanese (jw)", "Khmer (km)", "Latvian (lv)", "Lithuanian (lt)", 
    "Macedonian (mk)", "Polish (pl)", "Pashto (ps)", "Romanian (ro)", "Serbian (sr)", 
    "Slovak (sk)", "Slovenian (sl)", "Sundanese (su)", "Urdu (ur)")


# Helper function to download video and extract audio
def download_video_audio_separately(youtube_url, video_output_path, audio_output_path):
    # yt-dlp options for downloading audio and video separately
    ydl_opts = {
        'format': 'bestvideo',  # Download the best available video
        'outtmpl': video_output_path,  # Output path for the video
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    ydl_opts = {
        'format': 'bestaudio',  # Download the best available audio
        'outtmpl': audio_output_path,  # Output path for the audio
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

# Helper function to transcribe audio
def transcribe_audio(audio_path, model):
    segments, _ = model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments)

# Helper function for text-to-speech conversion
def text_to_speech(translated_text, output_audio_file, language='en'):
    tts = gTTS(text=translated_text, lang=language)
    tts.save(output_audio_file)

# Process Button
if st.button("Translate"):
    if youtube_url:
        try:
            # Step 1: Download Video and Audio Separately
            st.write("Downloading video and extracting audio...")
            video_path = "video.mp4"
            audio_path = "audio.mp3"
            download_video_audio_separately(youtube_url, video_path, audio_path)

            # Step 2: Transcribe Audio directly from MP3 (no conversion needed)
            st.write("Transcribing audio...")
            whisper_model = WhisperModel("base")
            transcription = transcribe_audio(audio_path, whisper_model)  # Use the audio.mp3 directly

            # Step 3: Translate Transcription
            st.write("Translating transcription...")
            translated_text = GoogleTranslator(source='auto', target=output_language).translate(transcription)

            # Step 4: Generate Translated Audio
            st.write("Generating translated audio...")
            translated_audio_path = "translated_audio.mp3"
            text_to_speech(translated_text, translated_audio_path, language=output_language)

            # Step 5: Provide Download Link for Translated Audio (without modifying video)
            st.success("Translation completed! Download the translated audio below.")
            st.audio(translated_audio_path, format='audio/mp3')
            st.download_button(
                label="Download Translated Audio",
                data=open(translated_audio_path, "rb"),
                file_name="translated_audio.mp3",
                mime="audio/mp3"
            )

            # Cleanup temporary files
            os.remove(audio_path)
            os.remove(video_path)
            os.remove(translated_audio_path)

        except yt_dlp.utils.DownloadError:
            st.error("Failed to download video. Please check the URL or try again later.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid YouTube URL.")
