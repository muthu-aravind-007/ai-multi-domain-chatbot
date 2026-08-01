from modules.llm.ollama import generate as ollama_generate
from modules.llm.gemini import generate as gemini_generate

def generate(prompt, provider):

    if provider == "gemini":
        return gemini_generate(prompt)

    return ollama_generate(prompt)