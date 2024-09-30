# Chat with Image 🖼️

## Overview

This project is a Streamlit application that allows users to upload an image and interact with it through a chat interface. The application utilizes the Groq API to generate responses based on user prompts related to the uploaded image.

## Features

- Upload images in formats such as JPG, JPEG, or PNG.
- Select between different AI models for generating responses.
- View chat history between the user and the assistant.
- A clean and modern UI styled with Tailwind CSS.

## Technologies Used

- **Python**: Main programming language.
- **Streamlit**: Framework for building the web application.
- **Groq**: API for generating responses based on images and prompts.
- **Tailwind CSS**: CSS framework for styling the UI.
- **dotenv**: For loading environment variables.

## Installation

### Prerequisites

- Python 3.10 
- An active Groq API key

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Hassn11q/chat-with-image.git
   cd chat-with-image
2. **Install the required packages:**
you can install the required packages using pip:
```bash
pip install -r requirements.txt
```
3. **Set up environment variables:**
Create a .env file in the root directory of the project and add your Groq API key:
```bash
GROQ_API_KEY=your_api_key
```
4. **Run the application:**
```bash
streamlit run app.py
```
5. **Access the application:**
Open your web browser and navigate to localhost to access the application.
