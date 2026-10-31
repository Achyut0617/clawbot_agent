
"""Offline text-to-speech for the Clawbot agent."""

import pyttsx3


def speak(text: str) -> None:
    """Speak a message aloud using the local system speech engine."""
    if not isinstance(text, str) or not text.strip():
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


if __name__ == "__main__":
    speak("Clawbot text to speech is working.")
