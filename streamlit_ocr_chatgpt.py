import streamlit as st
from PIL import Image, ImageGrab
import pytesseract
import openai
import tempfile
import os

# ---------------- CONFIG ----------------
# Set Tesseract path for Streamlit Cloud or local
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Change if running locally on Windows

# OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Global buffer for accumulated prompt
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""

# ---------------- OCR FUNCTION ----------------
def ocr_image(img):
    try:
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"Error OCRing image: {e}"

def process_uploaded_images(uploaded_files):
    for uploaded_file in uploaded_files:
        try:
            img = Image.open(uploaded_file)
            text = ocr_image(img)
            st.session_state.accumulated_prompt += text + "\n"
            st.markdown(f"**--- OCR for {uploaded_file.name} ---**")
            st.text(text)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

# ---------------- CHATGPT FUNCTION ----------------
def send_to_chatgpt():
    additional_text = st.session_state.additional_prompt.strip()
    if additional_text:
        st.session_state.accumulated_prompt += additional_text + "\n"
        st.session_state.additional_prompt = ""

    if not st.session_state.accumulated_prompt.strip():
        st.warning("No text to send. Add images or text first.")
        return

    st.markdown("--- Sending Prompt to ChatGPT ---")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": st.session_state.accumulated_prompt}],
            temperature=0.7
        )
        chat_response = response['choices'][0]['message']['content'].strip()
        st.markdown("**ChatGPT Response:**")
        st.text(chat_response)
        st.session_state.accumulated_prompt = ""  # Clear buffer after sending
    except Exception as e:
        st.error(f"Error contacting ChatGPT: {e}")

# ---------------- CLEAR FUNCTION ----------------
def clear_all():
    st.session_state.accumulated_prompt = ""
    st.session_state.additional_prompt = ""
    st.experimental_rerun()

# ---------------- STREAMLIT LAYOUT ----------------
st.title("📸 OCR + ChatGPT Web App")

# File uploader (multi)
uploaded_files = st.file_uploader(
    "Select images to OCR (PNG, JPG, JPEG, BMP, TIFF)",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)
if uploaded_files:
    process_uploaded_images(uploaded_files)

# Optional: Paste from clipboard (only works locally)
if st.button("Paste image from clipboard (local only)"):
    try:
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            text = ocr_image(img)
            st.session_state.accumulated_prompt += text + "\n"
            st.markdown(f"**--- OCR for Clipboard Image ---**")
            st.text(text)
        else:
            st.warning("Clipboard does not contain an image.")
    except Exception as e:
        st.error(f"Error reading clipboard image: {e}")

# Additional prompt
st.session_state.additional_prompt = st.text_area(
    "Add Text / Prompt Before Sending",
    value=st.session_state.get("additional_prompt", ""),
    height=100
)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Send to ChatGPT"):
        send_to_chatgpt()
with col2:
    if st.button("Clear All"):
        clear_all()
with col3:
    st.write("")  # empty column for spacing
