from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
import base64
from PIL import Image
import io

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
CORS(app)  # Allow requests from your HTML page

@app.route('/')
def index():
    return "Manga API is running. Use POST /generate to generate a manga page."

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    story_prompt = data.get('story', '')
    style_prompt = data.get('style', 'shoujo manga style, soft colors, detailed backgrounds')
    character_desc = data.get('character', 'a girl with long blue hair and round glasses, wearing a red scarf')
    prompt = (
        "A complete Japanese manga page layout, black and white, with 3-4 complete panels that fit entirely within the page boundaries. "
        "Each panel must be fully visible with complete panel borders - no panels should be cut off at the top, bottom, or sides of the page. "
        "Arrange the panels in a traditional Japanese manga layout (right to left, top to bottom reading order). "
        "Leave adequate margins around all panels so they are completely contained within the page. "
        "Each panel should show a complete scene with full character bodies and complete backgrounds visible. "
        "DO NOT include any speech bubbles, text, dialogue, or onomatopoeia in the image. "
        "Show only the visual story panels with characters and backgrounds. "
        "Ensure all panels are complete rectangles with clear, unbroken borders. "
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
        return jsonify({"error": "No image data returned."}), 500
    image_bytes = base64.b64decode(image_base64)
    return send_file(io.BytesIO(image_bytes), mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5001, debug=True) 