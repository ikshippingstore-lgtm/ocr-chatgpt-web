import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import openai

# ---------------- CONFIG ----------------
# Initialize EasyOCR Reader (English)
reader = easyocr.Reader(['en'], gpu=False)

# OpenAI API key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Session state buffers
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""
if "additional_prompt" not in st.session_state:
    st.session_state.additional_prompt = ""

# ---------------- OCR FUNCTION ----------------
def ocr_image(img: Image.Image):
    try:
        # Convert to RGB
        img = img.convert('RGB')

        # Resize for faster OCR if image is wide
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size)

        # EasyOCR
        text_list = reader.readtext(np.array(img), detail=0)
        return "\n".join(text_list)
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
st.title("📸 OCR + ChatGPT Web App")

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
    "Add Text / Prompt Befor
