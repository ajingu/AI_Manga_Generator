import os
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import requests
import base64
from PIL import Image
import io

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_manga_image(story_prompt: str, style_prompt: str, character_desc: str):
    prompt = (
        "A Japanese manga page, black and white, with clear panel borders. "
        "Arrange the panels so that the story is read from right to left, top to bottom, like a traditional Japanese manga. "
        "Draw empty speech bubbles for dialogue, but do not write any text inside them. "
        "Leave space for onomatopoeia text, but do not write any onomatopoeia. "
        f"Story: {story_prompt} "
        f"Main character: {character_desc} "
        f"Style: {style_prompt} "
    )
    api_prompt = prompt
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=api_prompt,
            size="1024x1024",
            n=1
        )
        image_base64 = response.data[0].b64_json
        if not image_base64:
            with open("error_log.txt", "w") as f:
                f.write(f"No image data returned. Full API response:\n{response}\n")
            return "Error: No image data returned. See error_log.txt for details."
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        return image
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(f"Error: {e}\n")
            if 'api_prompt' in locals():
                f.write(f"Prompt sent to API: {api_prompt}\n")
        return "Error generating manga page. See error_log.txt for details."

demo = gr.Interface(
    fn=generate_manga_image,
    inputs=[
        gr.Textbox(label="Story Prompt", lines=4, placeholder="Describe your manga story..."),
        gr.Textbox(label="Style Prompt", value="shoujo manga style, soft colors, detailed backgrounds"),
        gr.Textbox(label="Character Description", value="a girl with long blue hair and round glasses, wearing a red scarf"),
    ],
    outputs=gr.Image(label="Generated Manga Page"),
    title="Simple Manga Page Generator (gpt-image-1)",
    description="Generate a single manga page image using gpt-image-1. Enter your story, style, and character.",
    examples=[
        [
            "A young girl discovers a magical cat in her garden. The cat leads her to a hidden door. Inside, she finds a room full of ancient books. The books begin to glow with magical energy.",
            "shoujo manga style, soft colors, magical atmosphere",
            "a girl with long blue hair and round glasses, wearing a red scarf"
        ],
        [
            "A samurai prepares for battle. He draws his sword. He faces his opponent. They clash in a dramatic fight.",
            "seinen manga style, dynamic action, dramatic lighting",
            "a samurai with a topknot and a red kimono"
        ]
    ]
)

if __name__ == "__main__":
    demo.launch() 