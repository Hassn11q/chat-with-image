import os
import base64
import streamlit as st
from groq import Groq
from mistralai import Mistral
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Constants
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

# Streamlit Configuration
st.set_page_config(page_title="Chat with Image", page_icon="🖼️", layout="centered")

# Initialize Groq and Mistral Clients using caching to avoid reinitializing
@st.cache_resource
def initialize_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

@st.cache_resource
def initialize_mistral_client():
    return Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

groq_client = initialize_groq_client()
mistral_client = initialize_mistral_client()

# System Message Configuration
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a helpful assistant.",
}

def encode_image(image):
    """Encode an image to a base64 string."""
    return base64.b64encode(image.read()).decode("utf-8")

def is_image(filename):
    """Check if the file has an image extension."""
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def all_images(files):
    """Check if all uploaded files are images and count them."""
    return all(is_image(file.name) for file in files) and len(files) <= 3

def prepare_content_with_images(content: str, images: List[object]):
    """Prepare content with images for display."""
    return [{"type": "text", "text": content}] + [{"type": "image_url", "image_url": {"url": image}} for image in images]

def file_upload():
    """Handle file uploads and display uploaded images."""
    st.sidebar.header("Upload Files")
    uploaded_files = st.sidebar.file_uploader(
        "Upload up to 3 images...",
        type=IMAGE_EXTENSIONS,
        accept_multiple_files=True,
    )

    if uploaded_files and all_images(uploaded_files):
        with st.spinner("Processing images..."):
            encoded_images = [encode_image(image) for image in uploaded_files]
            st.sidebar.image(uploaded_files, use_column_width=True)
            return uploaded_files, encoded_images
    else:
        if uploaded_files:
            st.error("Please upload up to 3 images with valid extensions: " + ", ".join(IMAGE_EXTENSIONS))
        return None, None

def get_image_response_groq(image, prompt, model):
    """Request an image response from the GROQ API."""
    try:
        image_base64 = encode_image(image)
        image_url = f"data:image/jpeg;base64,{image_base64}"

        completion = groq_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0.0,
            max_tokens=256,
            top_p=1,
            stream=False,
            stop=None
        )

        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error with GROQ API: {str(e)}")
        return None

def get_image_response_mistral(image, prompt, model):
    """Request an image response from the Mistral API."""
    try:
        image_base64 = encode_image(image)
        image_url = f"data:image/jpeg;base64,{image_base64}"

        completion = mistral_client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0.0,
            max_tokens=256,
            top_p=1,
            stream=False,
            stop=None
        )

        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error with Mistral API: {str(e)}")
        return None

def main():
    """Main application logic."""
    # Custom HTML Example
    custom_html = """
    <div style="text-align: center; background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
        <h1 style="color: #4CAF50;">Chat with Image🖼️</h1>
        <p style="font-size: 15px;">Upload images and ask questions about them.</p>
        <div class="footer">
            Developed with ❤️ by Hassn | 
            <a href="https://github.com/Hassn11q" target="_blank" class="text-blue-600 hover:underline">GitHub</a>
        </div>
    </div>
    """

    st.markdown(custom_html, unsafe_allow_html=True)

    model = st.sidebar.selectbox(
        "Select Model",
        ("llama-3.2-11b-vision-preview", "llava-v1.5-7b-4096-preview", "pixtral-12b-2409")
    )
    
    # Modify system prompt
    st.sidebar.header("System Prompt")
    system_prompt = st.sidebar.text_area("Modify the system prompt", value=SYSTEM_MESSAGE["content"])
    SYSTEM_MESSAGE["content"] = system_prompt

    uploaded_files, encoded_images = file_upload()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Clear chat history
    if st.session_state.messages:
        if st.sidebar.button("Clear chat history"):
            st.session_state.messages.clear()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                if isinstance(content, list):
                    st.markdown(content[0]['text'])
                else:
                    st.markdown(content)
    
    # Handle user input
    if prompt := st.chat_input("Ask something", key="prompt"):
        content = prepare_content_with_images(prompt, encoded_images) if encoded_images else prompt

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": content})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Fetch assistant response
        with st.spinner("Generating response..."):
            response = None
            if uploaded_files:
                if model == "pixtral-12b-2409":
                    response = get_image_response_mistral(uploaded_files[0], prompt, model)
                else:
                    response = get_image_response_groq(uploaded_files[0], prompt, model)
            
            # If no image is uploaded, generate a regular text-based response
            if not response:
                messages = [SYSTEM_MESSAGE, *st.session_state.messages]
                client = mistral_client if model == "pixtral-12b-2409" else groq_client
                try:
                    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
                    response = st.write_stream(stream)  
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    return

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
