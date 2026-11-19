from __future__ import annotations

import queue
import threading
from collections.abc import Callable

from .asr import VoskStreamingRecognizer
from .audio import MicrophoneStream
from .interruption import InterruptionController
from .vad import VADConfig, VoiceActivitySegmenter


class VoiceInteraction:
    \"\"\"Hotkey-controlled microphone -> VAD -> Vosk -> final transcript pipeline.\"\"\"

    def __init__(
        self,
        model_path: str,
        on_final_transcript: Callable[[str], None],
        sample_rate: int = 16000,
        device: int | None = None,
    ) -> None:
        self.model_path = model_path
        self.on_final_transcript = on_final_transcript
        self.sample_rate = sample_rate
        self.device = device
        self.interruptions = InterruptionController()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._active = False

    @property
    def listening(self) -> bool:
        return self._active

    def toggle(self) -> None:
        with self._lock:
            if self._active:
                self.stop_listening()
            else:
                self.start_listening()

    def start_listening(self) -> None:
        with self._lock:
            if self._active:
                return
            self._active = True
            self._stop.clear()
            token = self.interruptions.begin()
            self._thread = threading.Thread(
                target=self._run, args=(token,), daemon=True, name="clawbot-voice"
            )
            self._thread.start()
        print("[ClawBot] Listening. Press the hotkey again to stop.")

    def stop_listening(self) -> None:
        self._stop.set()
        self.interruptions.interrupt()
        with self._lock:
            self._active = False
        print("[ClawBot] Listening stopped.")

    def _run(self, token) -> None:
        mic = MicrophoneStream(sample_rate=self.sample_rate, frame_ms=20, device=self.device)
        vad = VoiceActivitySegmenter(VADConfig(sample_rate=self.sample_rate, frame_ms=20))
        recognizer = VoskStreamingRecognizer(self.model_path, self.sample_rate)
        try:
            mic.start()
            while not self._stop.is_set() and not token.cancelled:
                try:
                    frame = mic.read(timeout=0.25)
                except queue.Empty:
                    continue
                for event in vad.process(frame):
                    if event.kind == "speech_frame":
                        transcript = recognizer.accept(event.pcm)
                        if transcript and transcript.kind == "partial":
                            print(f"\\r[You, partial] {transcript.text}", end="", flush=True)
                    elif event.kind == "speech_end":
                        # Feed the complete VAD segment to a fresh recognizer so the
                        # final transcript is isolated to this utterance.
                        utterance_recognizer = VoskStreamingRecognizer(
                            self.model_path, self.sample_rate
                        )
                        result = utterance_recognizer.accept(event.pcm)
                        final = utterance_recognizer.finish()
                        text = (final.text if final else "") or (result.text if result else "")
                        if text.strip():
                            print(f"\\n[You] {text}")
                            self.on_final_transcript(text.strip())
                        recognizer = VoskStreamingRecognizer(self.model_path, self.sample_rate)
        except Exception as exc:
            print(f"\\n[ClawBot audio error] {exc}")
            print("[ClawBot] Text interface remains available.")
        finally:
            mic.stop()
            vad.flush()
            self.interruptions.finish(token)
            with self._lock:
                self._active = False
