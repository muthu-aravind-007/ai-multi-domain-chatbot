import google.generativeai as genai
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Try configuring Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False


def analyze_image(image: Image.Image):
    """
    Hybrid image understanding:
    1. Try Gemini
    2. Fallback to OCR
    """

    # -----------------------------
    # TRY GEMINI
    # -----------------------------
    if GEMINI_AVAILABLE:
        try:
            response = model.generate_content([
                "Describe this image clearly for an AI assistant.",
                image
            ])
            return response.text
        except Exception as e:
            print("⚠️ Gemini failed, switching to fallback:", e)

    # -----------------------------
    # FALLBACK (OCR)
    # -----------------------------
    try:
        text = pytesseract.image_to_string(image)

        if text.strip():
            return f"Extracted text from image: {text}"

        return "Image content could not be clearly understood."
    except:
        return "Failed to process image."