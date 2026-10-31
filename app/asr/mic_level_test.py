import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

seconds = 5
device = sd.default.device[0]
info = sd.query_devices(device, "input")
rate = int(info["default_samplerate"])

print("Microphone:", info["name"])
print("Sample rate:", rate)
print("Speak normally for 5 seconds...")

audio = sd.rec(
    int(seconds * rate),
    samplerate=rate,
    channels=1,
    dtype="int16",
    device=device,
)
sd.wait()

write("logs\mic_check.wav", rate, audio)

samples = audio.astype(np.float64)
peak = np.max(np.abs(samples))
rms = np.sqrt(np.mean(samples ** 2))
print(f"Peak level: {peak:.0f} / 32768")
print(f"RMS level: {rms:.0f}")
print("Saved recording to logs\mic_check.wav")
