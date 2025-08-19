# streamlit_ocr_chatgpt.py
import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import openai

# ---------------- CONFIG ----------------
# Initialize EasyOCR once
reader = easyocr.Reader(['en'], gpu=False)

# OpenAI API key from Streamlit secrets
# Make sure to add your key in Streamlit Cloud: Secrets -> OPENAI_API_KEY
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""
if "additional_prompt" not in st.session_state:
    st.session_state.additional_prompt = ""

# ---------------- OCR FUNCTION ----------------
def ocr_image(uploaded_file):
    try:
        img = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(img)
        result = reader.readtext(img_array, detail=0)
        return "\n".join(result)
    except Exception as e:
        return f"Error OCRing image: {e}"

def process_uploaded_images(uploaded_files):
    for uploaded_file in uploaded_files:
        text = ocr_image(uploaded_file)
        st.session_state.accumulated_prompt += text + "\n"
        st.markdown(f"**--- OCR for {uploaded_file.name} ---**")
        st.text(text)

# ---------------- CHATGPT FUNCTION ----------------
def send_to_chatgpt():
    # Add additional prompt
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
        # Clear after sending
        st.session_state.accumulated_prompt = ""
    except Exception as e:
        st.error(f"Error contacting ChatGPT: {e}")

# ---------------- CLEAR FUNCTION ----------------
def clear_all():
    st.session_state.accumulated_prompt = ""
    st.session_state.additional_prompt = ""
    st.experimental_rerun()

# ---------------- STREAMLIT LAYOUT ----------------
st.title("📸 EasyOCR + ChatGPT Web App")

# File uploader (multi)
uploaded_files = st.file_uploader(
    "Select images to OCR (PNG, JPG, JPEG, BMP, TIFF)",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)
if uploaded_files:
    process_uploaded_images(uploaded_files)

# Additional prompt
st.session_state.additional_prompt = st.text_area(
    "Add Text / Prompt Before Sending",
    value=st.session_state.get("additional_prompt", ""),
    height=100
)

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Send to ChatGPT"):
        send_to_chatgpt()
with col2:
    if st.button("Clear All"):
        clear_all()
