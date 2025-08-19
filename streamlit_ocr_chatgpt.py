import streamlit as st
from PIL import Image
import easyocr
import openai
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="OCR + ChatGPT Web App", layout="wide")

# OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Session state buffer for accumulated prompt
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""
if "additional_prompt" not in st.session_state:
    st.session_state.additional_prompt = ""

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'], gpu=False)  # gpu=True if your environment supports GPU

# ---------------- OCR FUNCTION ----------------
def ocr_image(img: Image.Image):
    try:
        img_array = np.array(img)
        text_list = reader.readtext(img_array, detail=0)  # detail=0 returns only text
        return "\n".join(text_list)
    except Exception as e:
        return f"Error OCRing image: {e}"

def process_uploaded_images(uploaded_files):
    for uploaded_file in uploaded_files:
        try:
            img = Image.open(uploaded_file).convert("RGB")
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
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": st.session_state.accumulated_prompt}],
            temperature=0.7
        )
        chat_response = response.choices[0].message.content.strip()
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
st.title("📸 OCR + ChatGPT Web App (Online Friendly)")

# File uploader
uploaded_files = st.file_uploader(
    "Select images to OCR (PNG, JPG, JPEG, BMP, TIFF)",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)
if uploaded_files:
    process_uploaded_images(uploaded_files)

# Additional prompt text
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
