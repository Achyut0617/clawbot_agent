from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import webrtcvad


@dataclass(frozen=True)
class VADConfig:
    sample_rate: int = 16000
    frame_ms: int = 20
    aggressiveness: int = 2
    end_silence_ms: int = 700
    min_speech_ms: int = 150
    max_utterance_ms: int = 30000
    padding_ms: int = 200


@dataclass(frozen=True)
class VADSegment:
    kind: Literal["speech_start", "speech_frame", "speech_end"]
    pcm: bytes = b""
    speech_duration_ms: int = 0


class VoiceActivitySegmenter:
    \"\"\"WebRTC VAD segmenter. Input must be mono signed 16-bit PCM at a supported rate.\"\"\"

    SUPPORTED_RATES = (8000, 16000, 32000, 48000)

    def __init__(self, config: VADConfig | None = None) -> None:
        self.config = config or VADConfig()
        c = self.config
        if c.sample_rate not in self.SUPPORTED_RATES:
            raise ValueError(f"Unsupported WebRTC VAD sample rate: {c.sample_rate}")
        if c.frame_ms not in (10, 20, 30):
            raise ValueError("frame_ms must be 10, 20, or 30")
        if not 0 <= c.aggressiveness <= 3:
            raise ValueError("aggressiveness must be between 0 and 3")
        self._vad = webrtcvad.Vad(c.aggressiveness)
        self._frame_bytes = int(c.sample_rate * c.frame_ms / 1000) * 2
        self._active = False
        self._speech_ms = 0
        self._silence_ms = 0
        self._frames: list[bytes] = []

    @property
    def frame_bytes(self) -> int:
        return self._frame_bytes

    def process(self, frame: bytes) -> list[VADSegment]:
        if len(frame) != self._frame_bytes:
            raise ValueError(f"Expected {self._frame_bytes} bytes per frame; got {len(frame)}")
        is_speech = self._vad.is_speech(frame, self.config.sample_rate)
        out: list[VADSegment] = []
        if is_speech:
            if not self._active:
                self._active = True
                self._speech_ms = 0
                self._silence_ms = 0
                self._frames = []
                out.append(VADSegment("speech_start"))
            self._speech_ms += self.config.frame_ms
            self._silence_ms = 0
            self._frames.append(frame)
            out.append(VADSegment("speech_frame", frame, self._speech_ms))
        elif self._active:
            self._silence_ms += self.config.frame_ms
            self._frames.append(frame)
            if self._silence_ms >= self.config.end_silence_ms:
                if self._speech_ms >= self.config.min_speech_ms:
                    out.append(VADSegment("speech_end", b"".join(self._frames), self._speech_ms))
                self.reset()
            elif self._speech_ms + self._silence_ms >= self.config.max_utterance_ms:
                out.append(VADSegment("speech_end", b"".join(self._frames), self._speech_ms))
                self.reset()
        return out

    def flush(self) -> VADSegment | None:
        if not self._active:
            return None
        segment = None
        if self._speech_ms >= self.config.min_speech_ms:
            segment = VADSegment("speech_end", b"".join(self._frames), self._speech_ms)
        self.reset()
        return segment

    def reset(self) -> None:
        self._active = False
        self._speech_ms = 0
        self._silence_ms = 0
        self._frames = []
