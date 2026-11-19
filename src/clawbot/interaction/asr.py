from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from vosk import KaldiRecognizer, Model


@dataclass(frozen=True)
class TranscriptEvent:
    kind: Literal["partial", "final"]
    text: str


class VoskStreamingRecognizer:
    \"\"\"Vosk streaming recognizer. Feed mono 16-bit PCM frames at model sample rate.\"\"\"

    def __init__(self, model_path: str | Path, sample_rate: int = 16000) -> None:
        path = Path(model_path)
        if not path.is_dir():
            raise FileNotFoundError(
                f"Vosk model directory not found: {path}. Download and extract a model first."
            )
        self.sample_rate = sample_rate
        self._model = Model(str(path))
        self._recognizer = KaldiRecognizer(self._model, float(sample_rate))
        self._recognizer.SetWords(True)

    def accept(self, pcm: bytes) -> TranscriptEvent | None:
        if self._recognizer.AcceptWaveform(pcm):
            result = json.loads(self._recognizer.Result())
            text = result.get("text", "").strip()
            return TranscriptEvent("final", text) if text else None
        partial = json.loads(self._recognizer.PartialResult()).get("partial", "").strip()
        return TranscriptEvent("partial", partial) if partial else None

    def finish(self) -> TranscriptEvent | None:
        result = json.loads(self._recognizer.FinalResult())
        text = result.get("text", "").strip()
        return TranscriptEvent("final", text) if text else None
