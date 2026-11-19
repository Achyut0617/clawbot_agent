from __future__ import annotations

import queue
import sounddevice as sd


class MicrophoneStream:
    \"\"\"Bounded microphone frame source. Frames are mono int16 PCM.\"\"\"

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_ms: int = 20,
        queue_frames: int = 100,
        device: int | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_samples = int(sample_rate * frame_ms / 1000)
        self.device = device
        self.frames: queue.Queue[bytes] = queue.Queue(maxsize=queue_frames)
        self.dropped_frames = 0
        self._stream = None

    def _callback(self, indata, frames, time_info, status) -> None:
        if status:
            # Do not print from the audio callback; consumer can inspect dropped_frames.
            pass
        data = bytes(indata)
        try:
            self.frames.put_nowait(data)
        except queue.Full:
            self.dropped_frames += 1

    def start(self) -> None:
        if self._stream is not None:
            return
        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_samples,
            device=self.device,
            channels=1,
            dtype="int16",
            callback=self._callback,
        )
        self._stream.start()

    def read(self, timeout: float = 0.5) -> bytes:
        return self.frames.get(timeout=timeout)

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        while not self.frames.empty():
            try:
                self.frames.get_nowait()
            except queue.Empty:
                break

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
