
"""Live voice input -> Vosk -> safety gate -> LLM -> confirmation -> simulation."""

import json
import queue
import sys
import time
from math import gcd

import sounddevice as sd
from scipy.signal import resample_poly
from vosk import Model, KaldiRecognizer

from app.tts.speaker import speak
from app.safety.instruction_gate import check_instruction
from app.llm.planner import generate_plan
from app.safety.validator import validate_plan
from app.robot.simulator import simulate_plan

MODEL_PATH = "models/vosk/vosk-model-small-en-us-0.15"
TARGET_RATE = 16000
RECORD_SECONDS = 6

audio_queue = queue.Queue()


def say(message: str) -> None:
    """Speak a message without letting TTS failure interrupt safety checks."""
    try:
        speak(message)
    except Exception as exc:
        print(f"TTS unavailable: {exc}")


def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())


def recognize_voice():
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, TARGET_RATE)

    device = sd.default.device[0]
    info = sd.query_devices(device, "input")
    source_rate = int(info["default_samplerate"])

    print(f"Microphone: {info['name']}")
    print(f"Speak your command after the prompt ({RECORD_SECONDS} seconds).")

    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break

    with sd.InputStream(
        device=device,
        samplerate=source_rate,
        channels=1,
        dtype="int16",
        callback=audio_callback,
    ):
        start = time.monotonic()

        while time.monotonic() - start < RECORD_SECONDS:
            try:
                chunk = audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            samples = chunk[:, 0]

            if source_rate != TARGET_RATE:
                divisor = gcd(source_rate, TARGET_RATE)
                samples = resample_poly(
                    samples.astype("float32"),
                    TARGET_RATE // divisor,
                    source_rate // divisor,
                )
                samples = samples.clip(-32768, 32767).astype("int16")

            recognizer.AcceptWaveform(samples.tobytes())

    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip()


def main():
    input("Press Enter, then speak clearly...")

    try:
        text = recognize_voice()
    except Exception as exc:
        print(f"Microphone/ASR failed; nothing executed: {exc}")
        say("Speech recognition failed. Nothing executed.")
        return

    print(f"\nRecognized text: {text!r}")

    if not text:
        print("No speech recognized. Nothing executed.")
        say("I didn't recognize a command. Please try again.")
        return

    say(f"I heard: {text}")

    allowed, message = check_instruction(text)
    if not allowed:
        print(f"CLARIFICATION REQUIRED: {message}")
        say(f"Please clarify your command. {message}")
        return

    try:
        plan = generate_plan(text)
    except Exception as exc:
        print(f"LLM failed; nothing executed: {exc}")
        say("I couldn't generate a plan. Nothing executed.")
        return

    print("\nModel proposed:")
    print(json.dumps(plan, indent=2))

    checked = validate_plan(plan)
    if not checked["ok"]:
        print("REJECTED by safety validator:")
        for error in checked["errors"]:
            print(f"- {error}")
        print("Nothing executed.")
        say("The proposed plan was rejected by the safety validator. Nothing executed.")
        return

    print("\nPlease compare the recognized text and proposed plan.")
    print("If either is incorrect or uncertain, do not approve.")
    say("Please check the recognized command and proposed plan. Only approve if both are correct.")

    try:
        confirmation = input(
            "Type EXECUTE to approve this plan for SIMULATION ONLY: "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nNo confirmation received. Nothing executed.")
        say("No confirmation received. Nothing executed.")
        return

    if confirmation != "EXECUTE":
        print("Plan not approved. Nothing executed.")
        say("Plan not approved. Nothing executed.")
        return

    print("\nSimulation only — no physical hardware commands:")
    try:
        result = simulate_plan(plan)
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Simulation failed: {exc}")
        say("The simulation failed.")
        return

    say("Simulation completed. No physical robot action was performed.")


if __name__ == "__main__":
    main()
