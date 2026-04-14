from deep_translator import GoogleTranslator
from langdetect import detect


def detect_language(text):
    try:
        # Tamil detection
        if any('\u0B80' <= c <= '\u0BFF' for c in text):
            return "ta"

        # Hindi detection
        if any('\u0900' <= c <= '\u097F' for c in text):
            return "hi"

        # English default if mostly ASCII
        if all(ord(c) < 128 for c in text):
            return "en"

        # fallback
        from langdetect import detect
        return detect(text)

    except:
        return "en"


def translate_to_english(text):
    try:
        lang = detect_language(text)

        if lang == "en":
            return text

        return GoogleTranslator(source=lang, target='en').translate(text)
    except:
        return text


def translate_from_english(text, target_lang):
    try:
        if target_lang == "en":
            return text

        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except:
        return text