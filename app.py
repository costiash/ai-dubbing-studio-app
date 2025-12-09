
import streamlit as st
import os
from openai import OpenAI
from pydub import AudioSegment
import tempfile

# --- Page Config ---
st.set_page_config(page_title="AI Dubbing Studio", page_icon="🎙️", layout="centered")

# --- Session State ---
if "transcription_text" not in st.session_state:
    st.session_state.transcription_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "api_client" not in st.session_state:
    st.session_state.api_client = None

# --- Helpers ---
def validate_api_key(key):
    try:
        client = OpenAI(api_key=key)
        client.models.list()
        return client, True
    except:
        return None, False

def convert_to_mp3(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_in:
        tmp_in.write(uploaded_file.getvalue())
        input_path = tmp_in.name
    output_path = input_path.rsplit(".", 1)[0] + ".mp3"
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3")
    return output_path

# --- Sidebar ---
st.sidebar.header("⚙️ Configuration")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
if st.sidebar.button("Validate Key") and api_key_input:
    client, is_valid = validate_api_key(api_key_input)
    if is_valid:
        st.session_state.api_client = client
        st.sidebar.success("✅ Key Validated!")
    else:
        st.sidebar.error("❌ Invalid Key")

if st.session_state.api_client:
    st.sidebar.markdown("---")
    tts_model = st.sidebar.selectbox("TTS Model", ["tts-1", "tts-1-hd"])
    tts_voice = st.sidebar.selectbox("Voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], index=3)

# --- Main UI ---
st.title("🎙️ AI Dubbing Studio")
st.info("Upload audio -> Edit Transcript -> Translate -> Listen")

uploaded_file = st.file_uploader("Upload Audio", type=["ogg", "mp3", "wav", "m4a"])
col1, col2 = st.columns(2)
input_lang = col1.text_input("Input Language", "Hebrew")
output_lang = col2.text_input("Output Language", "Russian")

# Step 1: Transcribe
if uploaded_file and st.session_state.api_client:
    if st.button("📝 Step 1: Transcribe Audio"):
        with st.spinner("Transcribing..."):
            try:
                mp3_path = convert_to_mp3(uploaded_file)
                with open(mp3_path, "rb") as audio_file:
                    transcript = st.session_state.api_client.audio.transcriptions.create(
                        model="gpt-4o-transcribe", 
                        file=audio_file, 
                        response_format="json"
                    )
                # Handle response safely
                res_text = transcript.text if hasattr(transcript, 'text') else transcript['text']
                st.session_state.transcription_text = res_text
                st.success("Done!")
            except Exception as e:
                st.error(f"Error: {e}")

# Step 2: Edit & Translate
if st.session_state.transcription_text:
    st.markdown("---")
    st.subheader("✏️ Edit Transcript")
    edited_text = st.text_area("Correct any errors before translation:", st.session_state.transcription_text)
    st.session_state.transcription_text = edited_text

    if st.button("🌍 Step 2: Translate & Speak"):
        with st.spinner("Translating (GPT-5.1) & Generating Speech..."):
            try:
                # Translate
                trans_resp = st.session_state.api_client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[
                        {"role": "system", "content": f"Translate {input_lang} to {output_lang}. Be natural."},
                        {"role": "user", "content": st.session_state.transcription_text}
                    ]
                )
                trans_text = trans_resp.choices[0].message.content
                st.session_state.translated_text = trans_text
                
                # TTS
                speech_resp = st.session_state.api_client.audio.speech.create(
                    model=tts_model, voice=tts_voice, input=trans_text
                )
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    for chunk in speech_resp.iter_bytes(): tmp.write(chunk)
                    st.session_state.audio_path = tmp.name
                st.success("Complete!")
            except Exception as e:
                st.error(f"Error: {e}")

# Step 3: Result
if st.session_state.translated_text and st.session_state.audio_path:
    st.markdown("---")
    st.subheader("🎧 Result")
    st.text_area("Translation", st.session_state.translated_text)
    st.audio(st.session_state.audio_path)
    with open(st.session_state.audio_path, "rb") as f:
        st.download_button("Download MP3", f, "dubbed.mp3", "audio/mp3")
