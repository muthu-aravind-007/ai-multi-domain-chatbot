import os
import requests
import base64
import io
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print("🔥 USING GEMINI FILE:", __file__)


# -----------------------------
# GET AVAILABLE MODEL
# -----------------------------
def get_available_model():
    url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        print("❌ Failed to fetch models:", res.text)
        return None

    models = res.json().get("models", [])

    for m in models:
        name = m["name"]

        # We need model that supports generateContent
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print("✅ USING MODEL:", name)
            return name.replace("models/", "")

    return None


MODEL_NAME = get_available_model()


def analyze_image(image: Image.Image):
    try:
        if not MODEL_NAME:
            return "❌ No supported Gemini model found."

        # Convert RGBA → RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Describe this image clearly and in detail."},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            return f"❌ Gemini API error: {response.text}"

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Gemini failed: {str(e)}"