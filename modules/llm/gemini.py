import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def get_available_model():
    url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        models = response.json().get("models", [])

        for model in models:
            if "generateContent" in model.get("supportedGenerationMethods", []):
                return model["name"].replace("models/", "")

    except Exception as e:
        print(f"Gemini model discovery failed: {e}")

    return None


MODEL_NAME = get_available_model()


def generate(prompt):
    try:
        if not API_KEY:
            return "❌ GEMINI_API_KEY not found."

        if not MODEL_NAME:
            return "❌ No Gemini text model available."

        url = (
            f"https://generativelanguage.googleapis.com/v1/models/"
            f"{MODEL_NAME}:generateContent?key={API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"