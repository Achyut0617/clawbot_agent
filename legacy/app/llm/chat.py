"""Local Ollama conversation and request routing."""
import json
import urllib.request

MODEL = "qwen2.5:1.5b"
API_URL = "http://localhost:11434/api/chat"

def _ask(messages, json_mode=False):
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "options": {"temperature": 0.1}}
    if json_mode:
        payload["format"] = "json"
    request = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["message"]["content"].strip()

def route_request(text):
    """Use the local LLM to classify a request as chat or robot."""
    result = _ask([
        {"role": "system", "content": (
            'Classify the user request. Return JSON only: '
            '{"type":"chat"} for ordinary questions/conversation, or '
            '{"type":"robot"} only when the user explicitly requests a '
            'robot action such as moving, turning, stopping, or opening/'
            'closing the claw. Do not invent actions.')},
        {"role": "user", "content": text}
    ], json_mode=True)
    try:
        kind = json.loads(result).get("type")
    except (ValueError, AttributeError):
        kind = None
    return kind if kind in {"chat", "robot"} else "chat"

def chat(text):
    """Generate a normal conversational answer using local Ollama."""
    return _ask([
        {"role": "system", "content": (
            "You are Clawbot, a helpful local assistant. Answer naturally "
            "and concisely. Never claim a robot action happened unless the "
            "application reports its simulation result. You cannot control "
            "physical hardware in this application.")},
        {"role": "user", "content": text}
    ])
