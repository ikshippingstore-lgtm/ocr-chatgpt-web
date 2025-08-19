# streamlit_ocr_chatgpt.py
import streamlit as st
from PIL import Image
import pytesseract
import openai
import io

# ---------- CONFIG ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust for your server
openai.api_key = "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"  # Keep this secret, do NOT expose in frontend

# ---------- APP STATE ----------
if 'accumulated_prompt' not in st.session_state:
    st.session_state['accumulated_prompt'] = ""

# ---------- FUNCTIONS ----------
def ocr_image(img: Image.Image) -> str:
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"Error OCRing image: {e}"

def send_to_chatgpt(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error contacting ChatGPT: {e}"

# ---------- STREAMLIT UI ----------
st.title("OCR + ChatGPT Web Tool")
st.markdown("Upload images or paste them as files, add extra prompt text, and send to ChatGPT.")

# File uploader (multiple images)
uploaded_files = st.file_uploader("Upload Images", type=["png","jpg","jpeg","bmp","tiff"], accept_multiple_files=True)

for uploaded_file in uploaded_files:
    img = Image.open(uploaded_file)
    text = ocr_image(img)
    st.session_state['accumulated_prompt'] += text + "\n"
    st.markdown(f"**--- OCR for {uploaded_file.name} ---**")
    st.text(text)

# Additional text box
additional_text = st.text_area("Add extra prompt text (optional)")

# Buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Send to ChatGPT"):
        if additional_text:
            st.session_state['accumulated_prompt'] += additional_text + "\n"
        if st.session_state['accumulated_prompt'].strip() == "":
            st.warning("No text to send. Add images or prompt text first.")
        else:
            st.markdown("**--- Sending Prompt to ChatGPT ---**")
            chat_response = send_to_chatgpt(st.session_state['accumulated_prompt'])
            st.text(chat_response)
            st.session_state['accumulated_prompt'] = ""  # Clear after sending

with col2:
    if st.button("Clear All"):
        st.session_state['accumulated_prompt'] = ""
        st.experimental_rerun()

with col3:
    if st.button("Copy All OCR + Prompt"):
        import pyperclip
        pyperclip.copy(st.session_state['accumulated_prompt'])
        st.success("Copied to clipboard!")

# Display accumulated prompt for reference
if st.session_state['accumulated_prompt']:
    st.markdown("### Accumulated Prompt (preview)")
    st.text(st.session_state['accumulated_prompt'])
