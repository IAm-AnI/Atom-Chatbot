import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from PIL import Image
from gtts import gTTS
import tempfile

# Set the page configuration at the beginning
st.set_page_config(page_title="Atom Chatbot v-1")

# Load environment variables
load_dotenv()

# Load logo for chatbot response
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "chatbot_logo.png")

# Configure Generative AI model
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
image_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize chat in session state if not already done
if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    initial_prompt = "Your name is Atom. You are a chat assistant which is right now in initial state of development, currently version 1. You are created by Aniket Chaudhary."
    st.session_state.chat.send_message(initial_prompt, stream=False)

# Initialize response in session state if not already done
if 'response' not in st.session_state:
    st.session_state.response = ""

def get_gemini_response(question, image):
    if question and image:
        response = image_model.generate_content([question, image])
    elif question:
        response = st.session_state.chat.send_message(question, stream=True)
    elif image:
        response = image_model.generate_content([image])
    else:
        response = ""
    return response

# Function to set the theme
def set_theme(theme):
    if theme == 'dark':
        st._config.set_option('theme.base', 'dark')
        st._config.set_option('theme.backgroundColor', 'black')
        st._config.set_option('theme.secondaryBackgroundColor', 'brown')
        st._config.set_option('theme.textColor', 'white')
        st.session_state.themebutton = 'dark'
    else:
        st._config.set_option('theme.base', 'light')
        st._config.set_option('theme.backgroundColor', 'white')
        st._config.set_option('theme.secondaryBackgroundColor', '#ebfdff')
        st._config.set_option('theme.textColor', '#0a1464')
        st.session_state.themebutton = 'light'

# Initialize theme in session state
if 'themebutton' not in st.session_state:
    st.session_state['themebutton'] = 'light'
set_theme(st.session_state['themebutton'])

# Header with theme toggle switch
st.markdown("""
    <div style="display: flex; align-items: center;">
        <h2>ATOM Chatbot v1</h2>
        <p style="margin-top: auto;">Powered by Gemini LLM</p>
    </div>
    <div>
        <p style="color: grey; font-size: 12px;">Created by Aniket Chaudhary</p>
    </div>
""", unsafe_allow_html=True)

switch_label = 'Dark Mode' if st.session_state['themebutton'] == 'light' else 'Light Mode'
switch_value = st.session_state['themebutton'] == 'dark'

if st.checkbox(switch_label, value=switch_value):
    new_theme = 'dark' if st.session_state.themebutton == 'light' else 'light'
    set_theme(new_theme)

# Main content

# Input bar at the bottom with enter button
def submit_input():
    st.session_state.submit_button = True

input_text = st.text_input("Input: ", key="input", on_change=submit_input)
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.session_state.get('submit_button', False)

if submit and (input_text or image):
    response = get_gemini_response(input_text, image)
    if hasattr(response, '__iter__'):
        st.session_state.response = "".join(chunk.text for chunk in response)
    else:
        st.session_state.response = response
    st.session_state.submit_button = False
    
    # Convert the response to audio
    try:
        tts = gTTS(st.session_state.response)
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio_file.name)
        st.session_state.audio_file = temp_audio_file.name
    except Exception as e:
        st.error(f"An error occurred while generating the audio: {e}")
        print(f"An error occurred while generating the audio: {e}")

# Display the latest response with logo and play audio
if st.session_state.response:
    st.image(image_path, width=50)
    st.write(st.session_state.response)
    if 'audio_file' in st.session_state:
        try:
            with open(st.session_state.audio_file, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
        except FileNotFoundError:
            st.error(f"Audio file {st.session_state.audio_file} not found.")
        except Exception as e:
            st.error(f"An error occurred while playing the audio: {e}")
