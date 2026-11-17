
"""Central Clawbot controller: local LLM, voice, TTS, and simulation."""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request

from app.llm.chat import route_request, chat
from app.llm.planner import generate_plan
from app.safety.validator import validate_plan
from app.robot.simulator import simulate_plan
from app.tts.speaker import speak

OLLAMA_URL = os.getenv(
    "OLLAMA_URL", "http://127.0.0.1:11434"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")


def say(text: str) -> None:
    """Print and speak a message using offline TTS."""
    if not isinstance(text, str) or not text.strip():
        return

    print(f"\nClawbot: {text}")

    try:
        speak(text)
    except Exception as exc:
        print(f"[TTS ERROR] {exc}")


def ollama_ready() -> bool:
    """Return True when the local Ollama API responds."""
    try:
        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def ensure_ollama() -> bool:
    """Check Ollama, start it on Windows if needed, and verify the model."""
    print("\n[LLM] Checking local Ollama service...")

    if not ollama_ready():
        print("[LLM] Ollama API is not responding. Trying to start Ollama...")

        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if os.name == "nt" else 0
                ),
            )
        except FileNotFoundError:
            print("[LLM ERROR] Ollama executable was not found.")
            print("Install Ollama or add it to your PATH.")
            return False
        except OSError as exc:
            print(f"[LLM ERROR] Could not start Ollama: {exc}")
            return False

    # Wait up to 30 seconds for the local server.
    for attempt in range(30):
        if ollama_ready():
            print("[LLM] Ollama API is ready.")
            break
        time.sleep(1)
    else:
        print("[LLM ERROR] Ollama did not become ready within 30 seconds.")
        print("Try running 'ollama serve' manually to inspect its errors.")
        return False

    # Confirm the requested model is already installed.
    try:
        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        installed = {
            item.get("name", "")
            for item in data.get("models", [])
        }

        if OLLAMA_MODEL not in installed:
            print(f"[LLM ERROR] Model '{OLLAMA_MODEL}' is not installed.")
            print(f"Install it with: ollama pull {OLLAMA_MODEL}")
            return False

        print(f"[LLM] Local model available: {OLLAMA_MODEL}")
        return True

    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"[LLM ERROR] Could not inspect installed models: {exc}")
        return False


def process_text(text: str) -> None:
    """Route text to conversation or robot simulation."""
    text = text.strip()

    if not text:
        say("I didn't receive a command. Please try again.")
        return

    print(f"\nYou: {text}")

    try:
        kind = route_request(text)
    except Exception as exc:
        print(f"[ROUTER ERROR] {exc}")
        say("I could not process your request using the local language model.")
        return

    if kind == "chat":
        try:
            answer = chat(text)
            say(answer)
        except Exception as exc:
            print(f"[CHAT ERROR] {exc}")
            say("I could not generate a response.")
        return

    if kind != "robot":
        print(f"[ROUTER ERROR] Unexpected route: {kind!r}")
        say("I could not determine how to handle that request.")
        return

    try:
        plan = generate_plan(text)

        print("\nProposed robot plan:")
        print(json.dumps(plan, indent=2))

        checked = validate_plan(plan)

        if not checked.get("ok", False):
            print("Plan rejected:")
            for error in checked.get("errors", ["Unknown validation error"]):
                print(f"- {error}")
            say("The robot action plan was rejected.")
            return

        result = simulate_plan(plan)

        if result is not None:
            print("\nSimulation result:")
            print(json.dumps(result, indent=2, default=str))

        say("Simulation completed. No physical robot was controlled.")

    except Exception as exc:
        print(f"[ROBOT ERROR] {exc}")
        say("The robot request could not be completed.")


def voice_once() -> None:
    """Capture and process one voice command."""
    try:
        from app.voice_main import recognize_voice

        say("Listening for your command.")
        text = recognize_voice()

        if not text or not text.strip():
            say("I didn't recognize anything. Please try again.")
            return

        print(f"\nRecognized speech: {text}")
        process_text(text)

    except Exception as exc:
        print(f"[VOICE ERROR] {exc}")
        say("Voice input failed. Please check the microphone.")


def main() -> None:
    print("=" * 48)
    print("          CLAWBOT LOCAL AI AGENT")
    print("=" * 48)

    if not ensure_ollama():
        print("\nClawbot cannot start because the local LLM is unavailable.")
        return

    print("Conversation and planning: local Ollama")
    print("Speech output: offline TTS")
    print("Robot execution: simulation only")

    say("Clawbot is ready.")
    print("\nENTER = voice | C = typed chat | Q = quit")

    while True:
        try:
            choice = input("\n[ENTER / C / Q] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Clawbot.")
            say("Clawbot is shutting down.")
            break

        if choice == "q":
            say("Clawbot stopped.")
            break

        if choice == "":
            voice_once()
        elif choice == "c":
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                continue

            if text.lower() in {"/back", "/menu"}:
                continue

            process_text(text)
        else:
            say("Press Enter for voice, C for chat, or Q to quit.")


if __name__ == "__main__":
    main()
