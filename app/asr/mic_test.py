import json
import queue
import sys

import sounddevice as sd
from scipy.signal import resample_poly
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
RECORD_SECONDS = 6

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())


def main():
    print("Loading local speech model...")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    device = sd.default.device[0]
    device_info = sd.query_devices(device, "input")
    source_rate = int(device_info["default_samplerate"])

    print(f"Microphone: {device_info['name']}")
    print(f"Recording for {RECORD_SECONDS} seconds.")
    print("Say: 'Turn right for one second.'")

    with sd.InputStream(
        device=device,
        samplerate=source_rate,
        channels=1,
        dtype="int16",
        blocksize=0,
        callback=audio_callback,
    ):
        import time
        start = time.monotonic()

        while time.monotonic() - start < RECORD_SECONDS:
            try:
                chunk = audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            samples = chunk[:, 0]

            if source_rate != SAMPLE_RATE:
                from math import gcd
                divisor = gcd(source_rate, SAMPLE_RATE)
                samples = resample_poly(
                    samples.astype("float32"),
                    SAMPLE_RATE // divisor,
                    source_rate // divisor,
                )
                samples = samples.clip(-32768, 32767).astype("int16")

            if recognizer.AcceptWaveform(samples.tobytes()):
                print("Recognized:", json.loads(recognizer.Result()).get("text", ""))

    print("Final:", json.loads(recognizer.FinalResult()).get("text", ""))


if __name__ == "__main__":
    main()
