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
        return jsonify({"error": "No image data returned."}), 500
    image_bytes = base64.b64decode(image_base64)
    return send_file(io.BytesIO(image_bytes), mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5001, debug=True) 