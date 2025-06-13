import gradio as gr
from openai import OpenAI
import os
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import requests

# Suppress Intel MKL warning by using basic instruction set
os.environ['MKL_DEBUG_CPU_TYPE'] = '5'  # Use basic instruction set
os.environ['MKL_CBWR'] = 'COMPATIBLE'   # Use compatible mode

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_manga(prompt):
    # Add manga style to the prompt
    manga_prompt = f"manga style, {prompt}"
    
    try:
        # Generate image using DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=manga_prompt,
            size="1024x1024",
            quality="standard",  # DALL-E 3 only supports 'standard' and 'hd'
            n=1,
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image using requests
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Raise an exception for bad status codes
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_response.content))
        
        return image
        
    except Exception as e:
        print(f"Error details: {str(e)}")  # Print detailed error for debugging
        return f"Error generating image: {str(e)}"

# Create the Gradio interface
iface = gr.Interface(
    fn=generate_manga,
    inputs=gr.Textbox(label="Enter your prompt", placeholder="Describe the manga scene you want to generate..."),
    outputs=gr.Image(label="Generated Manga"),
    title="Manga AI Generator (DALL-E)",
    description="Generate manga-style images from text descriptions using DALL-E. Enter your prompt and click 'Submit' to generate an image.",
    examples=[
        ["A young samurai standing on a mountain peak at sunset"],
        ["A magical girl transforming with sparkles and ribbons"],
        ["A cyberpunk city street at night with neon signs"]
    ]
)

# Launch the app
if __name__ == "__main__":
    iface.launch() 