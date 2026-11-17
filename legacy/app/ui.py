
"""Clawbot dashboard: local voice input, planning, safety, TTS and simulation."""

import json
import urllib.request
from pathlib import Path
from math import gcd

import numpy as np
import sounddevice as sd
import streamlit as st
from scipy.signal import resample_poly
from vosk import Model, KaldiRecognizer

from app.llm.planner import generate_plan
from app.safety.instruction_gate import check_instruction
from app.safety.validator import validate_plan
from app.robot.simulator import simulate_plan
from app.tts.speaker import speak as tts_speak


ROOT = Path(__file__).resolve().parent.parent
VOSK_PATH = ROOT / "models" / "vosk" / "vosk-model-small-en-us-0.15"
SETTINGS_PATH = ROOT / "config" / "settings.json"
LOG_PATH = ROOT / "logs" / "ui_activity.log"

st.set_page_config(
    page_title="Clawbot Control Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: #0b111a;
    color: #e7edf5;
}
[data-testid="stSidebar"] {
    background: #111b28;
    border-right: 1px solid #263446;
}
.block-container {
    padding-top: 1.6rem;
    max-width: 1450px;
}
[data-testid="stMetric"] {
    background: #121e2c;
    border: 1px solid #26384b;
    border-radius: 12px;
    padding: 12px;
}
div.stButton > button {
    border-radius: 10px;
    min-height: 43px;
    font-weight: 600;
}
.small-muted {
    color: #93a6bb;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


def say(message):
    """Speak status messages; TTS errors must not interrupt safety checks."""
    try:
        tts_speak(message)
    except Exception as exc:
        st.warning(f"Speech output unavailable: {exc}")


def ollama_status():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
        names = [m.get("name", "") for m in data.get("models", [])]
        return True, names
    except Exception:
        return False, []


@st.cache_resource
def load_vosk():
    return Model(str(VOSK_PATH))


def capture_voice(seconds=6):
    device = sd.default.device[0]
    info = sd.query_devices(device, "input")
    source_rate = int(info["default_samplerate"])

    audio = sd.rec(
        int(seconds * source_rate),
        samplerate=source_rate,
        channels=1,
        dtype="int16",
        device=device,
    )
    sd.wait()

    samples = audio[:, 0]
    if source_rate != 16000:
        divisor = gcd(source_rate, 16000)
        samples = resample_poly(
            samples.astype(np.float32),
            16000 // divisor,
            source_rate // divisor,
        )
        samples = np.clip(samples, -32768, 32767).astype(np.int16)

    recognizer = KaldiRecognizer(load_vosk(), 16000)
    recognizer.AcceptWaveform(samples.tobytes())
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip(), info["name"]


def log_event(message):
    st.session_state.events.insert(0, message)
    st.session_state.events = st.session_state.events[:30]

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(message + "\n")
    except OSError:
        pass


def clear_results():
    st.session_state.plan = None
    st.session_state.validation = None
    st.session_state.simulation = None
    st.session_state.approved = False


for key, default in {
    "events": [],
    "command_text": "",
    "transcript": "",
    "plan": None,
    "validation": None,
    "simulation": None,
    "input_source": "Typed command",
    "approved": False,
    "last_error": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


online, model_names = ollama_status()
has_vosk = VOSK_PATH.is_dir()

try:
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig"))
except Exception:
    settings = {"mode": "simulation", "robot_hardware_enabled": False}

hardware_enabled = settings.get("robot_hardware_enabled", False)
simulation_mode = settings.get("mode", "simulation") == "simulation"

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 CLAWBOT")
    st.caption("LOCAL AGENT CONTROL CENTER")
    st.divider()

    st.markdown("### Component status")
    st.markdown(
        f"{'🟢' if online else '🔴'} **Ollama** — "
        f"{'Connected' if online else 'Offline'}"
    )
    st.markdown(
        f"{'🟢' if has_vosk else '🔴'} **Vosk ASR** — "
        f"{'Model available' if has_vosk else 'Model missing'}"
    )
    st.markdown("🟢 **Local TTS** — pyttsx3")
    st.markdown("🟢 **Safety validator** — enabled")
    st.markdown("🟢 **Robot simulator** — available")
    st.markdown("⚪ **NVIDIA Riva** — not integrated")
    st.markdown("⚪ **OpenClaw** — not integrated")

    st.divider()
    st.markdown("### Execution safety")
    st.info("Simulation only")
    st.caption("Physical robot commands are not supported by this dashboard.")

    if st.button("🔊 Test speech", use_container_width=True):
        say("Clawbot text to speech is working.")
        log_event("TTS test requested")

    if st.button("↻ Refresh component status", use_container_width=True):
        st.rerun()


# Header
st.title("Voice-Activated Clawbot Agent")
st.markdown(
    '<p class="small-muted">One-click command processing · Local AI · '
    'Automatic speech feedback · Human-approved simulation</p>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Local LLM", "Online" if online else "Offline")
m2.metric("Speech model", "Ready" if has_vosk else "Missing")
m3.metric("TTS", "Available")
m4.metric("Robot mode", "Simulation")

if not online:
    st.warning("Ollama is not reachable. Start Ollama before planning.")
if not has_vosk:
    st.warning(f"Vosk model not found: {VOSK_PATH}")
if hardware_enabled:
    st.error(
        "Hardware is enabled in settings. This dashboard refuses simulation "
        "approval until robot_hardware_enabled is false."
    )
if not simulation_mode:
    st.error("Settings are not in simulation mode. Simulation approval is disabled.")


command_tab, system_tab, activity_tab = st.tabs(
    ["🎙️ Command center", "⚙️ System status", "📋 Activity history"]
)


with command_tab:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("1. Enter or speak a command")

        if st.button("🎙️ Record voice · 6 seconds", use_container_width=True):
            if not has_vosk:
                st.error("The Vosk model is missing.")
            else:
                try:
                    with st.spinner("Listening... speak clearly now"):
                        transcript, mic_name = capture_voice()

                    st.session_state.transcript = transcript
                    st.session_state.command_text = transcript
                    st.session_state.input_source = "Microphone"
                    clear_results()

                    if transcript:
                        st.success(f"Recognized: {transcript}")
                        say(f"I heard: {transcript}")
                        log_event(f"Voice recognized: {transcript}")
                    else:
                        st.warning("No speech recognized. Try again.")
                        say("I didn't recognize a command. Please try again.")
                        log_event("Voice capture: no speech recognized")

                    st.caption(f"Microphone: {mic_name}")
                except Exception as exc:
                    st.error(f"Microphone error: {exc}")
                    say("Microphone input failed.")
                    log_event(f"Microphone error: {exc}")

        if st.session_state.transcript:
            st.info(
                f"Recognized speech: **{st.session_state.transcript}**\n\n"
                "Review it carefully; speech recognition can make mistakes."
            )

        st.text_area(
            "Command",
            key="command_text",
            height=110,
            placeholder="Example: Turn right for one second, then stop.",
        )

        st.checkbox(
            "I checked the command text and it matches my intention.",
            key="transcript_confirmed",
        )

        if st.button(
            "⚡ Process command",
            type="primary",
            use_container_width=True,
        ):
            clear_results()
            command = st.session_state.command_text.strip()

            if not command:
                st.error("Enter a command or record your voice first.")
                say("Please enter or speak a command.")
            elif not st.session_state.transcript_confirmed:
                st.warning("Confirm that the command text is correct first.")
                say("Please check and confirm the command text.")
            elif not online:
                st.error("Ollama is offline. No plan generated.")
                say("The language model is offline. Nothing executed.")
            elif not simulation_mode or hardware_enabled:
                st.error("Safe simulation settings are required.")
                say("Simulation settings are not safe. Nothing executed.")
            else:
                allowed, message = check_instruction(command)

                if not allowed:
                    st.warning(f"Clarification required: {message}")
                    say(f"Please clarify your command. {message}")
                    log_event(f"Clarification required: {command}")
                else:
                    try:
                        with st.spinner("Generating and validating the plan..."):
                            plan = generate_plan(command)
                            result = validate_plan(plan)

                        st.session_state.plan = plan
                        st.session_state.validation = result
                        st.session_state.approved = False
                        log_event(f"Plan generated: {command}")

                        if result["ok"]:
                            actions = result.get("actions", [])
                            say(
                                f"A plan with {len(actions)} actions was generated. "
                                "Please review it before approving simulation."
                            )
                        else:
                            say(
                                "The proposed plan was rejected by the safety validator. "
                                "Nothing executed."
                            )
                    except Exception as exc:
                        st.error(f"Planning failed: {exc}")
                        say("Planning failed. Nothing executed.")
                        log_event(f"Planning failed: {exc}")

    with right:
        st.subheader("2. Review and approve")

        if st.session_state.plan is None:
            st.markdown(
                """
                <div style="background:#121e2c;border:1px dashed #35485e;
                border-radius:14px;padding:28px;text-align:center;">
                <div style="font-size:32px;">⌘</div>
                <b>Ready for a command</b><br>
                <span style="color:#93a6bb;">
                Process a command to see the proposed actions here.
                </span></div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("**Proposed action plan**")
            st.json(st.session_state.plan)

            result = st.session_state.validation or {
                "ok": False,
                "errors": ["No validation result"],
            }

            if result.get("ok"):
                st.success(
                    f"Safety validation passed · "
                    f"{len(result.get('actions', []))} action(s)"
                )

                st.checkbox(
                    "I reviewed these exact actions and approve simulation.",
                    key="approve_plan",
                )

                if st.button(
                    "▶ Approve & simulate",
                    type="primary",
                    use_container_width=True,
                ):
                    if not st.session_state.get("approve_plan", False):
                        st.warning("Review and approve the proposed actions first.")
                        say("Please review and approve the plan first.")
                    elif not simulation_mode or hardware_enabled:
                        st.error("Unsafe settings. Simulation refused.")
                        say("Simulation refused because settings are unsafe.")
                    else:
                        try:
                            with st.spinner("Running simulation..."):
                                output = simulate_plan(st.session_state.plan)

                            st.session_state.simulation = output
                            st.session_state.approved = True
                            st.success("Simulation completed")
                            st.json(output)
                            say(
                                "Simulation completed. No physical robot action "
                                "was performed."
                            )
                            log_event("Simulation completed successfully")
                        except Exception as exc:
                            st.error(f"Simulation failed: {exc}")
                            say("The simulation failed.")
                            log_event(f"Simulation failed: {exc}")
            else:
                st.error("Plan rejected by the safety validator.")
                for error in result.get("errors", []):
                    st.write(f"• {error}")
                st.caption("Nothing was simulated.")
                say("The plan was rejected. Nothing executed.")

    if st.session_state.simulation:
        st.success("Last result: simulation only — physical motors were not used.")


with system_tab:
    st.subheader("Pipeline overview")

    stages = [
        ("01", "Microphone", "sounddevice", "Input capture"),
        ("02", "Speech recognition", "Vosk small English", "Local ASR"),
        ("03", "Language model", "Ollama · Qwen2.5 1.5B", "Local planning"),
        ("04", "Safety checks", "Instruction gate + validator", "Required"),
        ("05", "Robot output", "Python simulator", "Simulation only"),
        ("06", "Speech feedback", "pyttsx3", "Integrated into UI"),
    ]

    for number, title, detail, status in stages:
        with st.container(border=True):
            c1, c2, c3 = st.columns([0.12, 0.52, 0.36])
            c1.markdown(f"### {number}")
            c2.markdown(f"**{title}**")
            c2.caption(detail)
            c3.caption(status)

    st.subheader("Ollama models")
    if model_names:
        st.write(", ".join(model_names))
    else:
        st.write("No models reported by Ollama.")

    st.caption(
        "NVIDIA Riva, OpenClaw, and physical robot control are not integrated. "
        "A passing safety check does not guarantee physical-world safety."
    )


with activity_tab:
    st.subheader("Recent activity")

    if not st.session_state.events:
        st.info("No activity yet. Process a command to begin.")
    else:
        for event in st.session_state.events:
            st.markdown(f"- {event}")

    if st.button("Clear visible activity history"):
        st.session_state.events = []
        st.rerun()


st.divider()
st.caption(
    "Clawbot Agent · Local development dashboard · "
    "Explicit approval required · Simulation only · Physical motors disabled"
)
