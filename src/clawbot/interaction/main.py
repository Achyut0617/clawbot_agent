from __future__ import annotations

import argparse
import signal
import threading

from .controller import VoiceInteraction
from .hotkey import GlobalHotkey


def main() -> None:
    parser = argparse.ArgumentParser(description="ClawBot advanced interaction demo")
    parser.add_argument("--model-path", required=True, help="Path to an extracted Vosk model")
    parser.add_argument("--hotkey", default="ctrl+shift+space")
    parser.add_argument("--device", type=int, default=None)
    args = parser.parse_args()

    shutdown = threading.Event()

    def on_final_transcript(text: str) -> None:
        # INTEGRATION POINT:
        # Send this text to ClawBot's existing normalized request pipeline.
        # Do not invoke tools/capabilities directly from this callback.
        print(f"[VOICE REQUEST -> CONNECT YOUR CLAWBOT PIPELINE] {text}")

    interaction = VoiceInteraction(
        model_path=args.model_path,
        on_final_transcript=on_final_transcript,
        device=args.device,
    )
    hotkey = GlobalHotkey(args.hotkey, interaction.toggle)

    try:
        hotkey.register()
        print(f"[ClawBot] Global hotkey registered: {args.hotkey}")
        print("[ClawBot] Press Esc then Enter to quit. Text interaction remains separate.")
        while not shutdown.is_set():
            try:
                command = input()
            except EOFError:
                break
            if command.strip().lower() in {"esc", "exit", "quit"}:
                break
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"[ClawBot] Hotkey unavailable: {exc}")
        print("[ClawBot] You can still integrate VoiceInteraction with a UI button.")
    finally:
        interaction.stop_listening()
        hotkey.unregister()
        shutdown.set()


if __name__ == "__main__":
    main()
