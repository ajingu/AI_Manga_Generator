import os
from openai import OpenAI
from dotenv import load_dotenv
import base64
from PIL import Image
import io

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_manga_image(story_prompt, style_prompt, character_desc, output_path="manga_page.png"):
    prompt = (
        "A Japanese manga page, black and white, with clear panel borders. "
        "Arrange the panels so that the story is read from right to left, top to bottom, like a traditional Japanese manga. "
        f"Story: {story_prompt} "
        f"Main character: {character_desc} "
        f"Style: {style_prompt} "
    )
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    image_base64 = response.data[0].b64_json
    if not image_base64:
        print("No image data returned.")
        return
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes))
    image.save(output_path)
    print(f"Saved manga page to {output_path}")

if __name__ == "__main__":
    story = input("Enter your manga story: ")
    style = "shoujo manga style, soft colors, detailed backgrounds"
    character = "a girl with long blue hair and round glasses, wearing a red scarf"
    generate_manga_image(story, style, character) 