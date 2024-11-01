import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv
import speech_recognition as sr

# Load environment variables
load_dotenv()

# Configure the generative AI model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

def get_gemini_response(question):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(question)
    return response.text

def get_gemini_vision_response(input_text, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        if input_text:
            response = model.generate_content([input_text, image])
        else:
            response = model.generate_content(image)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def generate_image_from_text(prompt):
    # Note: This is a placeholder. Gemini doesn't currently support image generation.
    # You would need to use a different API (like DALL-E or Stable Diffusion) for this.
    st.warning("Image generation is not currently supported by Gemini. This is a placeholder.")
    # Placeholder: return a base64 encoded dummy image
    dummy_image = Image.new('RGB', (300, 300), color = 'red')
    buffered = io.BytesIO()
    dummy_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Speak now.")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech could not be understood"
    except sr.RequestError:
        return "Could not request results from the speech recognition service"

# Streamlit UI
st.title("AI Assistant")

# Sidebar for feature selection
feature = st.sidebar.selectbox("Choose a feature", ["Text Query", "Image Analysis", "Generate Image", "Voice Input"])

if feature == "Text Query":
    st.header("Text Query")
    input_text = st.text_input("Enter your question:")
    if st.button("Ask"):
        if input_text:
            with st.spinner("Generating response..."):
                response = get_gemini_response(input_text)
            st.subheader("Response:")
            st.write(response)
        else:
            st.warning("Please enter a question.")

elif feature == "Image Analysis":
    st.header("Image Analysis")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        input_text = st.text_input("Ask a question about the image (optional):")
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing..."):
                response = get_gemini_vision_response(input_text, image)
            st.subheader("Analysis Result:")
            st.write(response)

elif feature == "Generate Image":
    st.header("Generate Image from Text")
    image_prompt = st.text_input("Describe the image you want to generate:")
    if st.button("Generate Image"):
        if image_prompt:
            with st.spinner("Generating image..."):
                image_base64 = generate_image_from_text(image_prompt)
            st.subheader("Generated Image:")
            st.image(f"data:image/png;base64,{image_base64}", use_column_width=True)
        else:
            st.warning("Please enter an image description.")

elif feature == "Voice Input":
    st.header("Voice Input")
    if st.button("Start Voice Input"):
        with st.spinner("Listening..."):
            voice_text = speech_to_text()
        st.text_input("You said:", value=voice_text)
        if voice_text and voice_text != "Speech could not be understood":
            with st.spinner("Generating response..."):
                response = get_gemini_response(voice_text)
            st.subheader("Response:")
            st.write(response)