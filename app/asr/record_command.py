import sounddevice as sd
from scipy.io.wavfile import write

seconds = 5
device = sd.default.device[0]
info = sd.query_devices(device, "input")
rate = int(info["default_samplerate"])

print("Microphone:", info["name"])
print("Speak clearly: Turn right for one second.")
audio = sd.rec(
    int(seconds * rate),
    samplerate=rate,
    channels=1,
    dtype="int16",
    device=device,
)
sd.wait()

write("logs\voice_command.wav", rate, audio)
print("Saved fresh sample to logs\voice_command.wav")
