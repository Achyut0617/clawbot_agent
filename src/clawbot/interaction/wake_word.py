from __future__ import annotations


class OpenWakeWordDetector:
    \"\"\"Optional OpenWakeWord adapter. Pass the 16 kHz mono int16 PCM frames it expects.

    Install the optional dependencies with: pip install -e '.[wakeword]'.
    Verify the selected model name/path against the installed OpenWakeWord release.
    \"\"\"

    def __init__(self, model_path: str) -> None:
        if not model_path:
            raise ValueError("A wake-word model name or path is required")
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise RuntimeError(
                "OpenWakeWord is optional. Install with: pip install -e '.[wakeword]'"
            ) from exc
        self._model = Model(wakeword_models=[model_path], inference_framework="onnx")
        self._model_path = model_path

    def process(self, pcm16: bytes, threshold: float = 0.5) -> bool:
        import numpy as np

        audio = np.frombuffer(pcm16, dtype=np.int16)
        predictions = self._model.predict(audio)
        return any(float(score) >= threshold for score in predictions.values())

    def reset(self) -> None:
        self._model.reset()
