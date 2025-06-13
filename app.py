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

def generate_manga(prompt, model_choice):
    # Add manga style to the prompt
    manga_prompt = f"manga style, {prompt}"
    
    try:
        # Set parameters based on model choice
        if model_choice == "DALL-E 2":
            model = "dall-e-2"
            size = "512x512"  # Smallest size for DALL-E 2
            # Generate image using DALL-E 2 (no quality parameter)
            response = client.images.generate(
                model=model,
                prompt=manga_prompt,
                size=size,
                n=1,
            )
        else:  # DALL-E 3
            model = "dall-e-3"
            size = "1024x1024"
            # Generate image using DALL-E 3 (with quality parameter)
            response = client.images.generate(
                model=model,
                prompt=manga_prompt,
                size=size,
                quality="standard",  # Lowest quality for DALL-E 3
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
    inputs=[
        gr.Textbox(label="Enter your prompt", placeholder="Describe the manga scene you want to generate..."),
        gr.Dropdown(
            choices=["DALL-E 2", "DALL-E 3"],
            value="DALL-E 2",
            label="Select Model",
            info="DALL-E 2 is cheaper but lower quality. DALL-E 3 is more expensive but higher quality."
        )
    ],
    outputs=gr.Image(label="Generated Manga"),
    title="Manga AI Generator",
    description="""
    Generate manga-style images from text descriptions.
    - DALL-E 2: 512x512 pixels, cheaper ($0.02 per image)
    - DALL-E 3: 1024x1024 pixels, more expensive ($0.04 per image)
    Enter your prompt, select a model, and click 'Submit' to generate an image.
    """,
    examples=[
        ["A young samurai standing on a mountain peak at sunset", "DALL-E 2"],
        ["A magical girl transforming with sparkles and ribbons", "DALL-E 2"],
        ["A cyberpunk city street at night with neon signs", "DALL-E 3"]
    ]
)

# Launch the app
if __name__ == "__main__":
    iface.launch() 