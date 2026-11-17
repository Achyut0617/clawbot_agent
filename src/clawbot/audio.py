from pathlib import Path


class VoiceUnavailable(RuntimeError):
    pass


class VoiceInput:
    """Optional Vosk + sounddevice push-to-talk adapter; text input never depends on it."""

    def __init__(self, model_path: str, sample_rate: int = 16000, seconds: int = 6):
        self.model_path = Path(model_path)
        self.sample_rate = sample_rate
        self.seconds = seconds

    @staticmethod
    def microphone_available() -> bool:
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            return any(int(d.get("max_input_channels", 0)) > 0 for d in devices)
        except Exception:
            return False

    def listen_once(self) -> str:
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer, Model
        except ImportError as exc:
            raise VoiceUnavailable("Install voice extras: pip install -e '.[voice]'") from exc

        if not self.model_path.is_dir():
            raise VoiceUnavailable(f"Vosk model directory not found: {self.model_path}")
        try:
            model = Model(str(self.model_path))
            recognizer = KaldiRecognizer(model, self.sample_rate)
            audio = sd.rec(int(self.seconds * self.sample_rate), samplerate=self.sample_rate,
                           channels=1, dtype="int16")
            sd.wait()
            recognizer.AcceptWaveform(audio.tobytes())
            import json
            return json.loads(recognizer.FinalResult()).get("text", "").strip()
        except Exception as exc:
            raise VoiceUnavailable(f"Microphone/recognition unavailable: {exc}") from exc


def speak(text: str, enabled: bool = True) -> None:
    if not enabled:
        return
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception:
        # Audio output is optional; terminal output remains authoritative.
        return
