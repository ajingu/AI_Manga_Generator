# AI Manga Generator

A web application that uses AI to generate a single manga page from a story prompt. Users can then interactively add and edit speech bubbles with AI-generated dialogue onto the page.

https://github.com/user-attachments/assets/7223f016-7a3a-44c4-80b4-19f5233316a2

## Features

- **AI-Powered Image Generation**: Creates a manga page layout using OpenAI's DALL-E 3 model based on user prompts.
- **Customizable Prompts**: Allows users to define the story, art style, and main character descriptions.
- **Interactive Canvas**: An editable canvas using Fabric.js to place and manipulate speech bubbles.
- **Intelligent Bubble Placement**: An "Auto-Place" feature that analyzes the generated image to find manga panels and position speech bubbles automatically.
- **Contextual Dialogue Generation**: Automatically generates short, impactful dialogue for each bubble using GPT-4, based on the story and panel content.
- **Full Customization**: Users can add bubbles manually, clear all bubbles, and edit the AI-generated text.
- **Save & Export**: Download the final creation as a PNG image.

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, [Fabric.js](http://fabricjs.com/)
- **AI Models**:
  - Image Generation: OpenAI DALL-E 3 (`gpt-image-1`)
  - Dialogue Generation: OpenAI GPT-4
- **Python Libraries**: `openai`, `flask`, `flask-cors`, `python-dotenv`, `Pillow`, `gradio`

## Setup

Follow these steps to set up the project on your local machine.

1.  **Clone the repository:**
2.  **Create and activate a Conda or Python virtual environment:**
3.  **Install dependencies:**
    Install all the required Python packages using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

## Running the Application

The application consists of a Python Flask backend and an HTML/JS frontend.

1.  **Start the Backend API:**
    Open a terminal, navigate to the project directory, and run:

    ```bash
    python manga_api.py
    ```

    The backend server will start running on `http://localhost:5001`.

2.  **Open the Frontend:**
    In your file explorer, find the `manga_web.html` file and open it with a modern web browser (like Chrome, Firefox, or Edge).

## How to Use the Web Interface

1.  Enter the **Story**, **Art Style**, and **Main Character** details in the form on the left.
2.  Click the **"Generate Manga Page"** button.
3.  Wait for the AI to generate the manga image. Speech bubbles with AI-generated dialogue will be automatically placed on the image.
4.  **To edit dialogue**: Double-click on the text or the bubble itself.
5.  **To move/resize**: Single-click a bubble to select it, then drag to move or use the handles to resize. You can also move the text independently from its bubble.
6.  Use the control buttons for more actions:
    - **`+ Add Speech Bubble`**: Manually adds a new bubble to the center of the canvas.
    - **`🎯 Auto-Place Bubbles`**: Clears existing bubbles and runs the panel detection and dialogue generation again.
    - **`🗑️ Clear Bubbles`**: Removes all speech bubbles from the canvas.
    - **`💾 Save Image`**: Downloads the final manga page with your edits as a PNG file.

## Alternative Gradio UI

This project also includes a simpler, alternative UI built with Gradio for basic image generation without the interactive editor.

- **To run it:**
  ```bash
  python app.py
  ```
- Open the URL provided in the terminal (usually `http://127.0.0.1:7860`) in your browser.
