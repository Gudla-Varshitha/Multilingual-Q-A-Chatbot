import streamlit as st
import speech_recognition as sr
import pyttsx3
import os
import sys

# --- IMPORTANT FIX FOR IMPORTERROR ---
# Add the 'app' directory to the Python path
# This allows importing modules from 'app' correctly,
# resolving "attempted relative import with no known parent package" errors.
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
# ------------------------------------

# --- CORRECTED IMPORTS ---
# These imports now explicitly reference the 'app' package
from app.qa_pipeline import answer_question
from app.translate import translate_text
from app.detect_language import detect_language
# -------------------------

# Initialize TTS engine
# Note: pyttsx3 might require additional system dependencies (e.g., espeak on Linux, SAPI on Windows)
try:
    engine = pyttsx3.init()
except Exception as e:
    st.warning(f"Text-to-speech engine initialization failed: {e}. Speech output may not work.")
    engine = None

# Supported output languages (ISO 639-1 codes)
LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese": "zh", # Mandarin (Simplified)
    "Japanese": "ja",
    "Korean": "ko"
}

# --- STYLING IMPROVEMENTS: Page Configuration ---
st.set_page_config(
    page_title="🌍 Multilingual Q&A Chatbot",
    layout="centered", # Can be "wide" for more space
    initial_sidebar_state="auto",
    menu_items={
        'About': "A Multilingual Q&A Chatbot powered by Google's LLMs and Wikipedia."
    }
)

# --- STYLING IMPROVEMENTS: Custom CSS for Bright & Elegant Theme ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
        color: #333333 !important; /* Dark text for light background */
        /* Bright, animated linear gradient background */
        background: linear-gradient(135deg, #e0f2f7 0%, #d0e8f2 50%, #c0e0eb 100%) !important;
        background-size: 400% 400% !important; /* Larger size for animation */
        animation: gradientAnimation 18s ease infinite; /* Smooth, slow animation */
    }

    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background-color: rgba(230, 245, 250, 0.95) !important; /* Changed from white to light blue */
        border-radius: 25px; /* More rounded corners */
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15); /* Subtle shadow for light theme */
        padding: 2rem 1.5rem !important; /* Responsive padding */
        margin: 2rem auto !important; /* Responsive margin, auto centers */
        max-width: 800px; /* Max width for larger screens */
        width: 95%; /* Responsive width */
        border: 1px solid rgba(0, 0, 0, 0.05); /* Very subtle light border */
        backdrop-filter: none !important; /* Remove blur for bright theme */
        -webkit-backdrop-filter: none !important;
        transition: all 0.5s ease; /* Smooth transition for app container changes */
    }

    .reportview-container .main .block-container {
        padding-top: 1rem;
        padding-right: 1.5rem;
        padding-left: 1.5rem;
        padding-bottom: 1rem;
    }

    /* Header Styling */
    h1 {
        color: #007bff !important; /* Bright blue for title */
        text-align: center;
        font-size: 3.8em !important; /* Larger title */
        margin-bottom: 0.2em;
        text-shadow: 0 0 10px rgba(0, 123, 255, 0.3); /* Subtle blue glow */
        font-weight: 700 !important;
        letter-spacing: 1px;
    }

    h3 {
        color: #555555 !important; /* Darker gray for description */
        text-align: center;
        font-size: 1.6em !important;
        margin-bottom: 2.5em;
        font-weight: 400 !important;
        line-height: 1.5;
    }

    /* Streamlit specific text adjustments for light theme */
    .stMarkdown, .stText, .stRadio > label, .stSelectbox > label, .stTextInput > label, .stSelectbox [data-testid="stSelectbox"] > div > div > div {
        color: #333333 !important; /* Ensure all text is dark */
    }
    /* For the dropdown arrow */
    .stSelectbox [data-testid="stSelectboxChevron"] svg {
        fill: #333333 !important; /* Dark arrow */
    }


    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%) !important; /* Blue gradient */
        color: white !important;
        padding: 15px 30px !important; /* Larger padding */
        border-radius: 12px !important; /* More rounded */
        border: none !important;
        cursor: pointer !important;
        font-size: 1.2em !important;
        font-weight: 600 !important;
        transition: all 0.4s ease !important; /* Slower transition */
        box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4) !important; /* More pronounced shadow */
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0056b3 0%, #007bff 100%) !important;
        transform: translateY(-5px) scale(1.02) !important; /* More pronounced lift and slight scale */
        box-shadow: 0 12px 35px rgba(0, 123, 255, 0.6) !important;
    }
    .stButton>button:active {
        transform: translateY(0) scale(0.98) !important; /* Slight press effect */
        box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2) !important;
    }

    /* Input Field Styling */
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #f8f9fa !important; /* Very light gray background for inputs */
        color: #333333 !important; /* Dark text in inputs */
        border-radius: 12px !important; /* More rounded */
        padding: 15px !important; /* More padding */
        border: 1px solid #ced4da !important; /* Subtle gray border */
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.1) !important; /* Subtle inner shadow */
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div:focus {
        border-color: #007bff !important; /* Bright blue focus border */
        box-shadow: 0 0 0 0.3rem rgba(0, 123, 255, 0.25), inset 0 2px 8px rgba(0,0,0,0.15) !important; /* Stronger glow on focus and deeper inner shadow */
        outline: none !important;
    }

    /* Radio Button Styling - Targeting specific Streamlit classes */
    /* This targets the outer circle of the radio button */
    .stRadio > label > div[data-testid="stFlex"] > div:first-child {
        border: 2px solid #007bff !important; /* Bright blue border for unselected */
        background-color: #f8f9fa !important; /* Light background for the circle */
    }
    /* This targets the inner dot of the selected radio button */
    .stRadio > label > div[data-testid="stFlex"] > div:first-child > div {
        background-color: #FF6B6B !important; /* Vibrant red dot for selected */
    }


    /* Info/Success/Error Messages */
    .stAlert {
        border-radius: 15px !important; /* More rounded alerts */
        padding: 20px !important; /* More padding */
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        background-color: #e9f7fe !important; /* Light blue background for alerts */
        color: #0056b3 !important; /* Dark blue text */
        border: 1px solid #b3e0ff !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    .stAlert.info {
        border-left: 5px solid #007bff !important; /* Bright blue info border */
        background-color: #e0f7fa !important; /* Light cyan */
        color: #00796b !important; /* Dark cyan */
    }
    .stAlert.success {
        border-left: 5px solid #28a745 !important; /* Green success border */
        background-color: #e8f5e9 !important; /* Light green */
        color: #2e7d32 !important; /* Dark green */
    }
    .stAlert.error {
        border-left: 5px solid #dc3545 !important; /* Red error border */
        background-color: #ffebee !important; /* Light red */
        color: #c62828 !important; /* Dark red */
    }

    /* Separator */
    hr {
        border: 0 !important;
        height: 1px !important;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0)) !important;
        margin: 3em 0 !important;
    }

    /* Footer */
    .footer {
        text-align: center !important;
        margin-top: 40px !important;
        font-size: 1em !important;
        color: #777777 !important; /* Medium gray for footer */
        text-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HEADER SECTION with Emoji Logo ---
st.write("") # Add some space for top margin
st.title("🌍 Multilingual Q&A Chatbot")
st.markdown("### 🎙️ Ask a question using your voice or text, and get answers in your preferred language!")

st.markdown("---") # Visual separator

# --- INPUT SECTION ---
with st.container():
    st.markdown("Choose output language:")
    output_lang_name = st.selectbox("", list(LANGUAGES.keys()), key="output_lang_select", label_visibility="collapsed")
    output_lang_code = LANGUAGES[output_lang_name]

    st.markdown("Choose input method:")
    option = st.radio("", ["Type", "Speak"], key="input_method_radio", label_visibility="collapsed")

# Initialize session state for input and button states
if 'text_input_query' not in st.session_state:
    st.session_state.text_input_query = ""
if 'record_button_disabled' not in st.session_state:
    st.session_state.record_button_disabled = False
if 'speak_answer_button_disabled' not in st.session_state:
    st.session_state.speak_answer_button_disabled = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = None

def set_processing_state(is_processing):
    st.session_state.record_button_disabled = is_processing
    st.session_state.speak_answer_button_disabled = is_processing
    # The text input itself needs to be handled directly as st.text_input doesn't have 'disabled'
    # We'll control its value and re-render to simulate disable.

def clear_chat():
    st.session_state.chat_history = []
    st.session_state.text_input_query_value = "" # Clear input field too
    set_processing_state(False) # Ensure buttons are re-enabled
    # Removed: st.rerun() # This causes the "no-op" warning and is not needed here
    # Streamlit will naturally re-render on the next cycle, reflecting the cleared state.

def copy_answer_to_clipboard(answer_text):
    # This uses a workaround for Streamlit as direct clipboard access is limited
    st.code(f"Answer copied:\n{answer_text}", language="text")
    st.info("Answer copied to the clipboard (displayed above for verification).")


if option == "Type":
    # Use a callback for text input submission
    def handle_text_input_submit():
        if st.session_state.text_input_query_value:
            st.session_state.user_input_from_text = st.session_state.text_input_query_value
            st.session_state.text_input_query_value = "" # Clear input after submission
            set_processing_state(True) # Disable buttons
    
    st.text_input(
        "📝 Enter your question:", # Changed logo from ≡ to 📝
        key="text_input_query_value", # Use a unique key for the actual input value
        on_change=handle_text_input_submit,
        disabled=st.session_state.record_button_disabled # Disable if other buttons are disabled
    )
    user_input = st.session_state.get('user_input_from_text', None)

else: # option == "Speak"
    if st.button("🎙️ Record Voice Input", key="record_button", disabled=st.session_state.record_button_disabled):
        r = sr.Recognizer()
        with st.spinner("🎤 Listening... Speak now."):
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source) # Optional: adjust for noise
                    audio = r.listen(source)
                text = r.recognize_google(audio)
                st.success(f"You said: {text} 🎉")
                user_input = text
                set_processing_state(True) # Disable buttons after recording
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech. 😔")
                set_processing_state(False)
            except sr.RequestError as e:
                st.error(f"Speech recognition service error: {e} 😞")
                set_processing_state(False)
            except Exception as e:
                # --- Specific error handling for PyAudio ---
                if "PyAudio" in str(e):
                    st.error(
                        f"**PyAudio not found!** 🚨 To use speech input, you need to install PyAudio. "
                        f"Please follow these steps:\n\n"
                        f"1. **Install PortAudio** (system dependency):\n"
                        f"   - **Windows:** Download the pre-compiled wheel from "
                        f"     [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) "
                        f"     (find the correct version for your Python, e.g., `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`). "
                        f"     Then install it using `pip install path/to/your/downloaded/PyAudio‑*.whl`.\n"
                        f"   - **macOS:** `brew install portaudio` (if you have Homebrew)\n"
                        f"   - **Linux:** `sudo apt-get install portaudio19-dev`\n\n"
                        f"2. **Install PyAudio** (Python package):\n"
                        f"   `pip install PyAudio`\n\n"
                        f"After installation, restart your Streamlit app. 🛠️"
                    )
                else:
                    st.error(f"An unexpected error occurred during speech recognition: {e} 🚨")
                set_processing_state(False)

# --- ANSWER DISPLAY SECTION ---
if user_input:
    # Add user question to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    st.markdown("---") # Visual separator
    st.markdown("#### 💬 Chatbot Response:")
    try:
        # Detect input language
        input_lang_code = detect_language(user_input)
        st.info(f"Detected input language: **{input_lang_code}** 🌐")

        # Get answer using LLM
        with st.spinner("🧠 Getting answer..."):
            answer_raw = answer_question(user_input, input_lang_code)

        with st.spinner(f"🗣️ Translating answer to {output_lang_name}..."):
            answer_translated = translate_text(answer_raw, input_lang_code, output_lang_code)

        st.success(f"{answer_translated} ✨")
        st.session_state.chat_history.append({"role": "bot", "content": answer_translated})

        # Display chat history (newest at bottom)
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Chatbot:** {message['content']}")


        # Buttons for interaction with the answer
        col_speak, col_copy = st.columns(2)
        with col_speak:
            if engine and st.button("🔊 Speak Answer", key="speak_answer_button", disabled=st.session_state.speak_answer_button_disabled):
                try:
                    engine.setProperty('rate', 150) # You can adjust the speech rate
                    engine.say(answer_translated)
                    engine.runAndWait()
                except Exception as e:
                    st.error(f"Error speaking answer: {e} 🚫")
                finally:
                    set_processing_state(False) # Re-enable buttons after speaking
            elif not engine:
                st.warning("Speech output is not available. pyttsx3 engine failed to initialize. 🔇")
                set_processing_state(False) # Re-enable buttons if engine fails
        with col_copy:
            if st.button("📋 Copy Answer", key="copy_answer_button"):
                copy_answer_to_clipboard(answer_translated)
        
    except Exception as e:
        st.error(f"⚠️ An error occurred during processing: {e} Please ensure your API key is correct and Generative Language API is enabled. 🛠️")
        set_processing_state(False) # Re-enable buttons on error
    finally:
        # Ensure buttons are re-enabled if an error occurs before the speak button is pressed
        # Clear temporary user input from session state if it exists
        if 'user_input_from_text' in st.session_state:
            del st.session_state.user_input_from_text
        set_processing_state(False) # Always re-enable at the end of processing


st.markdown("---")
# Add a Clear Chat button at the bottom
st.button("🧹 Clear Chat", on_click=clear_chat, key="clear_chat_button")
st.markdown('<div class="footer">Created with ❤️ using Streamlit, Google LLMs, and Wikipedia.</div>', unsafe_allow_html=True)
