import streamlit as st
import speech_recognition as sr
import pyttsx3
import os
import sys
import datetime # Import datetime for timestamping download file

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

# Initialize chat history in session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add an initial welcome message to the history
    st.session_state.messages.append({"role": "bot", "content": "Hello! Ask me anything in any language, and I'll try to answer in your preferred output language."})

# Initialize selected output language in session state
if 'output_lang_selected' not in st.session_state:
    st.session_state.output_lang_selected = "English" # Default to English

# --- STYLING IMPROVEMENTS: Custom CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #333;
    }

    body {
        background: linear-gradient(135deg, #f0f2f5 0%, #e0e6ed 100%);
        background-attachment: fixed;
    }

    .stApp {
        background-color: transparent; /* Ensure Streamlit app background is transparent to show body gradient */
    }

    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        max-width: 800px; /* Constrain width for better aesthetics */
        margin: auto; /* Center the container */
    }

    /* Header Styling */
    h1 {
        color: #4CAF50; /* Green */
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    h3 {
        color: #555;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 1.5em;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 12px 25px;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        font-size: 1.1em;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Input Field Styling */
    .stTextInput>div>div>input, .stSelectbox>div>div {
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #ddd;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25);
        outline: none;
    }

    /* Radio Button Styling */
    .stRadio > label {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
    }

    /* Info/Success/Error Messages */
    .stAlert {
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .stAlert.info {
        background-color: #e0f7fa;
        color: #00796b;
        border-left: 5px solid #00bcd4;
    }
    .stAlert.success {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 5px solid #4CAF50;
    }
    .stAlert.error {
        background-color: #ffebee;
        color: #c62828;
        border-left: 5px solid #f44336;
    }

    /* Separator */
    hr {
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
        margin: 2em 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 0.9em;
        color: #777;
    }

    /* Chat message styling */
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .user-bubble {
        background-color: #e6f7ff; /* Light blue for user */
        color: #333;
        align-self: flex-end;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }

    .bot-bubble {
        background-color: #f0f0f0; /* Light grey for bot */
        color: #333;
        align-self: flex-start;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- STYLING IMPROVEMENTS: Header Section with Logo ---
# Removed the logo and adjusted the title to be directly centered
st.title("🌍 Multilingual Q&A Chatbot")
st.markdown("### 🎙️ Ask a question using your **voice or text**, and get answers in your preferred language!")

st.markdown("---") # Visual separator

# --- STYLING IMPROVEMENTS: Input Section ---
with st.container():
    st.markdown("#### 🗣️ Choose your preferences:")
    
    col1, col2 = st.columns(2)
    with col1:
        # Get the current index of the selected language
        current_lang_index = list(LANGUAGES.keys()).index(st.session_state.output_lang_selected)
        
        # Display the selectbox with the current language pre-selected
        output_lang_name = st.selectbox(
            "Choose output language:", 
            list(LANGUAGES.keys()), 
            index=current_lang_index, # Set the index of the currently selected language
            key="output_lang_select"
        )
        # Update the session state when a new language is selected
        st.session_state.output_lang_selected = output_lang_name
        output_lang_code = LANGUAGES[output_lang_name]
    with col2:
        option = st.radio("Choose input method:", ["Type", "Speak"], key="input_method_radio")

user_input = None

if option == "Type":
    user_input = st.text_input("🧾 Enter your question:", key="text_input_query")
else:
    # Speech recognition logic for Streamlit
    if st.button("🎙️ Record Voice Input", key="record_button"):
        r = sr.Recognizer()
        with st.spinner("🎤 Listening... Speak now."):
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source) # Optional: adjust for noise
                    audio = r.listen(source)
                text = r.recognize_google(audio)
                st.success(f"You said: {text} 🎉")
                user_input = text
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech. 😔")
            except sr.RequestError as e:
                st.error(f"Speech recognition service error: {e} 😞")
            except Exception as e:
                st.error(f"An unexpected error occurred during speech recognition: {e} 🚨")

# --- STYLING IMPROVEMENTS: Answer Display Section ---
if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Detect input language
        input_lang_code = detect_language(user_input)
        st.info(f"Detected input language: **{input_lang_code}** 🌐")

        # Get answer using LLM
        with st.spinner("🧠 Getting answer from LLM and Wikipedia..."):
            answer_raw = answer_question(user_input, input_lang_code)

        # Translate answer to preferred output language
        with st.spinner(f"🗣️ Translating answer to {output_lang_name}..."):
            answer_translated = translate_text(answer_raw, input_lang_code, output_lang_code)

        st.success(f"**Answer ({output_lang_name}):** {answer_translated} ✨")

        # Add bot message to history
        st.session_state.messages.append({"role": "bot", "content": answer_translated})

        # Speak answer button
        if engine and st.button("🔊 Speak Answer", key="speak_answer_button"):
            try:
                engine.setProperty('rate', 150) # You can adjust the speech rate
                engine.say(answer_translated)
                engine.runAndWait()
            except Exception as e:
                st.error(f"Error speaking answer: {e} 🚫")
        elif not engine:
            st.warning("Speech output is not available. pyttsx3 engine failed to initialize. 🔇")

    except Exception as e:
        st.error(f"⚠️ An error occurred during processing: {e} Please ensure your API key is correct and Generative Language API is enabled. 🛠️")

st.markdown("---") # Visual separator

# --- Display Chat History (Moved to Bottom) ---
st.markdown("#### 💬 Conversation History:")
chat_history_container = st.container(border=True) # Use a container for chat history
with chat_history_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# --- Chat Management Buttons (Moved to Bottom, below history) ---
col_chat_buttons = st.columns(2) # Create two columns for the buttons

with col_chat_buttons[0]:
    def clear_chat_history():
        st.session_state.messages = []
        st.session_state.messages.append({"role": "bot", "content": "Hello! Ask me anything in any language, and I'll try to answer in your preferred output language."})
    st.button("🧹 Clear Chat", on_click=clear_chat_history, key="clear_chat_button")

with col_chat_buttons[1]:
    def get_chat_history_as_text():
        history_text = ""
        for message in st.session_state.messages:
            history_text += f"{message['role'].capitalize()}: {message['content']}\n\n"
        return history_text

    # Generate a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_history_{timestamp}.txt"

    st.download_button(
        label="📥 Download Chat History",
        data=get_chat_history_as_text(),
        file_name=filename,
        mime="text/plain",
        key="download_chat_button"
    )

st.markdown("---")
st.markdown('<div class="footer">Created with ❤️ using Streamlit, Google LLMs, and Wikipedia.</div>', unsafe_allow_html=True)
