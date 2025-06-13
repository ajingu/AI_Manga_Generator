import gradio as gr
from openai import OpenAI
import os
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import requests
import textwrap
from typing import List, Tuple

# Suppress Intel MKL warning by using basic instruction set
os.environ['MKL_DEBUG_CPU_TYPE'] = '5'  # Use basic instruction set
os.environ['MKL_CBWR'] = 'COMPATIBLE'   # Use compatible mode

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def split_story_into_scenes(story: str, num_panels: int = 4) -> List[str]:
    """Split a story into multiple scenes for different panels."""
    # Use OpenAI to split the story into coherent scenes
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""You are a manga storyboard artist. 
                Split the given story into exactly {num_panels} distinct scenes that can be visualized.
                Each scene should be a single sentence that clearly describes what to draw.
                Focus on key moments and visual elements.
                Return only the scenes, one per line."""},
                {"role": "user", "content": story}
            ],
            temperature=0.7,
        )
        scenes = response.choices[0].message.content.strip().split('\n')
        # Ensure we have exactly num_panels scenes
        if len(scenes) > num_panels:
            scenes = scenes[:num_panels]
        while len(scenes) < num_panels:
            scenes.append(scenes[-1])  # Duplicate last scene if we don't have enough
        return scenes
    except Exception as e:
        print(f"Error splitting story: {str(e)}")
        # Fallback: simple sentence splitting
        sentences = story.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > num_panels:
            sentences = sentences[:num_panels]
        while len(sentences) < num_panels:
            sentences.append(sentences[-1])
        return sentences

def generate_panel(prompt: str, model: str, size: str, style_prompt: str) -> Image.Image:
    """Generate a single manga panel."""
    try:
        # Combine the scene prompt with the style prompt
        full_prompt = f"manga style, {style_prompt}, {prompt}"
        
        if model == "gpt-image-1":  # GPT-Image-1
            response = client.images.generate(
                model="gpt-image-1",
                prompt=full_prompt,
                size=size,
                n=1,
            )
        elif model == "dall-e-2":
            response = client.images.generate(
                model="dall-e-2",
                prompt=full_prompt,
                size=size,
                n=1,
            )
        else:  # DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size=size,
                quality="standard",
                n=1,
            )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        return Image.open(io.BytesIO(image_response.content))
    except Exception as e:
        print(f"Error generating panel: {str(e)}")
        raise

def create_manga_page(panels: List[Image.Image], layout: str = "2x2") -> Image.Image:
    """Arrange panels into a manga page layout."""
    if layout == "2x2":
        # Create a 2x2 grid
        width = max(panel.width for panel in panels)
        height = max(panel.height for panel in panels)
        page = Image.new('RGB', (width * 2, height * 2), 'white')
        
        # Place panels in 2x2 grid
        positions = [(0, 0), (width, 0), (0, height), (width, height)]
        for panel, pos in zip(panels, positions):
            # Resize panel to fit the grid
            panel = panel.resize((width, height), Image.Resampling.LANCZOS)
            page.paste(panel, pos)
    else:
        # Create a vertical strip (1x4)
        width = max(panel.width for panel in panels)
        height = max(panel.height for panel in panels)
        page = Image.new('RGB', (width, height * len(panels)), 'white')
        
        # Place panels vertically
        for i, panel in enumerate(panels):
            panel = panel.resize((width, height), Image.Resampling.LANCZOS)
            page.paste(panel, (0, i * height))
    
    return page

def generate_manga(story_prompt: str, model_choice: str, num_panels: int, layout: str, style_prompt: str):
    """Generate a complete manga page from a story prompt."""
    try:
        # Split story into scenes
        scenes = split_story_into_scenes(story_prompt, num_panels)
        
        # Set parameters based on model choice
        if model_choice == "GPT-Image-1":
            model = "gpt-image-1"
            size = "1024x1024"  # Using 512x512 for GPT-Image-1 as it's a good balance
        elif model_choice == "DALL-E 2":
            model = "dall-e-2"
            size = "512x512"  # Smallest size for DALL-E 2
        else:  # DALL-E 3
            model = "dall-e-3"
            size = "1024x1024"
        
        # Generate each panel
        panels = []
        for scene in scenes:
            panel = generate_panel(scene, model, size, style_prompt)
            panels.append(panel)
        
        # Create the final manga page
        manga_page = create_manga_page(panels, layout)
        
        return manga_page, "\n".join(f"Panel {i+1}: {scene}" for i, scene in enumerate(scenes))
        
    except Exception as e:
        print(f"Error details: {str(e)}")
        return f"Error generating manga: {str(e)}", ""

# Create the Gradio interface
iface = gr.Interface(
    fn=generate_manga,
    inputs=[
        gr.Textbox(
            label="Story Prompt",
            placeholder="Describe your manga story...",
            lines=3,
            info="Describe the complete story you want to tell. The AI will split it into panels."
        ),
        gr.Dropdown(
            choices=["GPT-Image-1", "DALL-E 2", "DALL-E 3"],
            value="DALL-E 2",
            label="Select Model",
            info="""Choose the model to use:
            - GPT-Image-1: Original model, 512x512 size ($0.016 per image)
            - DALL-E 2: Improved model, 512x512 size ($0.02 per image)
            - DALL-E 3: Latest model, 1024x1024 size ($0.04 per image)"""
        ),
        gr.Slider(
            minimum=2,
            maximum=4,
            value=4,
            step=1,
            label="Number of Panels",
            info="Choose how many panels to generate (2-4)"
        ),
        gr.Dropdown(
            choices=["2x2", "vertical"],
            value="2x2",
            label="Page Layout",
            info="Choose how to arrange the panels"
        ),
        gr.Textbox(
            label="Style Prompt",
            placeholder="shoujo manga style, soft colors, detailed backgrounds",
            value="shoujo manga style, soft colors, detailed backgrounds",
            info="Describe the visual style for all panels"
        )
    ],
    outputs=[
        gr.Image(label="Generated Manga Page"),
        gr.Textbox(label="Generated Scenes", lines=4)
    ],
    title="Manga Page Generator",
    description="""
    Generate a complete manga page with multiple panels telling a story.
    - Enter your story and the AI will split it into panels
    - Choose between GPT-Image-1 (512x512, $0.016), DALL-E 2 (512x512, $0.02), or DALL-E 3 (1024x1024, $0.04)
    - Select the number of panels and page layout
    - Add a style prompt to maintain consistent visual style
    """,
    examples=[
        [
            "A young girl discovers a magical cat in her garden. The cat leads her to a hidden door. Inside, she finds a room full of ancient books. The books begin to glow with magical energy.",
            "DALL-E 2",
            4,
            "2x2",
            "shoujo manga style, soft colors, magical atmosphere"
        ],
        [
            "A samurai prepares for battle. He draws his sword. He faces his opponent. They clash in a dramatic fight.",
            "DALL-E 3",
            4,
            "vertical",
            "seinen manga style, dynamic action, dramatic lighting"
        ],
        [
            "A robot wakes up in a junkyard. It finds a broken toy. It repairs the toy. The toy comes to life.",
            "GPT-Image-1",
            4,
            "2x2",
            "vintage manga style, mechanical details, warm lighting"
        ]
    ]
)

# Launch the app
if __name__ == "__main__":
    iface.launch() 