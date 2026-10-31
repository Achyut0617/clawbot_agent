from faster_whisper import WhisperModel

audio_path = "logs/voice_command.wav"

print("Loading Whisper base model on CPU...")
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
)

segments, info = model.transcribe(
    audio_path,
    language="en",
    beam_size=5,
    vad_filter=True,
)

print("Detected language:", info.language)
print("Transcription:")
text_parts = []

for segment in segments:
    text_parts.append(segment.text.strip())
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text.strip()}")

print("\nFinal:", " ".join(text_parts))

