from googletrans import Translator

translator = Translator()

def detect_language(text):
    try:
        return translator.detect(text).lang
    except:
        return "en"


def translate_to_english(text):
    try:
        return translator.translate(text, dest="en").text
    except:
        return text


def translate_from_english(text, target_lang):
    try:
        return translator.translate(text, dest=target_lang).text
    except:
        return text