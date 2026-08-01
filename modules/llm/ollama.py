import subprocess

def generate(prompt, model="mistral"):
    try:
        result = subprocess.run(
            ["ollama","run",model],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        return result.stdout.strip()

    except Exception as e:
        return f"Error generating response: {str(e)}"