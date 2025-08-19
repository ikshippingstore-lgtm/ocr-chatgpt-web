import streamlit as st
from PIL import Image
import easyocr
import openai
import io

# ---------------- CONFIG ----------------
# Initialize EasyOCR Reader once (CPU only for Streamlit Cloud)
reader = easyocr.Reader(['en'], gpu=False)

# OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Global accumulated prompt
if "accumulated_prompt" not in st.session_state:
    st.session_state.accumulated_prompt = ""

# ---------------- HELPER FUNCTIONS ----------------
def resize_image(img, max_width=1000):
    """Resize image proportionally to max_width"""
    if img.width > max_width:
        w_percent = max_width / float(img.width)
        h_size = int(img.height * w_percent)
        return img.resize((max_width, h_size), Image.ANTIALIAS)
    return img

def ocr_image(img):
    """Perform OCR using EasyOCR"""
    img = resize_image(img)
    try:
        result = reader.readtext(np.array(img), detail=0)
        return "\n".join(result)
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

def clear_all():
    st.session_state.accumulated_prompt = ""
    st.session_state.additional_prompt = ""
    st.experimental_rerun()

# ---------------- STREAMLIT LAYOUT ----------------
st.title("📸 OCR + ChatGPT Web App (Faster Online)")

# File uploader
uploaded_files = st.file_uploader(
    "Select images to OCR (PNG, JPG, JPEG, BMP, TIFF)",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing images..."):
        process_uploaded_images(uploaded_files)

# Additional prompt text
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
