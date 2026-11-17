import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

SYSTEM_PROMPT = """
You are the conversational assistant for a voice-activated robot project.
Answer ordinary questions naturally and concisely.
Do not claim that you moved or controlled physical hardware.
If the user requests a robot movement, explain that robot commands
must be handled by the project's existing motor-action planner.
"""

def chat(message: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()
