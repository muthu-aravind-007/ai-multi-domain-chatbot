import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.0-pro-vision")


def analyze_image(image):
    try:
        response = model.generate_content([
            "Describe this image clearly and in detail.",
            image
        ])
        return response.text

    except Exception as e:
        return f"❌ Gemini failed: {str(e)}"