import subprocess

def generate(prompt):
    result = subprocess.run(
        ["ollama", "run", "phi", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",     
        errors="ignore"       
    )
    return result.stdout.strip()