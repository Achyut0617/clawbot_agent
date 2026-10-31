\# Voice-Activated Clawbot Agent



\## Project Overview



A local voice-controlled robot-agent prototype developed on Windows. It combines speech recognition, local LLM-based action planning, safety validation, simulated robot actions, and text-to-speech feedback.



\*\*Current operating mode:\*\* Simulation only. Physical motor control is disabled.



\## Pipeline



\### Voice input

Microphone → Vosk speech recognition → instruction safety gate



\### Action planning

Recognized instruction → Ollama local LLM (`qwen2.5:1.5b`) → structured JSON action plan



\### Safety and execution

Structured plan → safety validator → explicit user confirmation in the voice pipeline → robot simulator



\### Speech feedback

Local TTS using `pyttsx3` → spoken status and feedback messages



The typed-input entry point (`app.main`) and voice-input entry point (`app.voice\_main`) provide separate ways to test the pipeline.



\## Implemented Components



\- \*\*ASR:\*\* Vosk with the local model at `models/vosk/vosk-model-small-en-us-0.15`

\- \*\*LLM:\*\* Ollama with `qwen2.5:1.5b`

\- \*\*Safety:\*\* Instruction gate and structured action-plan validation

\- \*\*Robot:\*\* Simulation-only action runner

\- \*\*TTS:\*\* Local speech output through `pyttsx3`

\- \*\*Tests:\*\* Automated unit tests for safety and plan validation



\## Validation Results



\- The automated test suite passed all 10 tests in the latest recorded run.

\- Typed-input test: `turn right for one second` produced a `turn\_right` action with a duration of 1000 ms.

\- The safety validator rejected an empty action list in a voice-pipeline test.

\- The standalone TTS test ran successfully.



Speech recognition accuracy has not been fully evaluated. The voice pipeline still requires a successful end-to-end test with a correctly recognized command and explicit confirmation.



\## Project Structure



\- `app/asr/` — speech recognition components

\- `app/llm/` — local LLM planning

\- `app/tts/` — text-to-speech

\- `app/robot/` — robot simulation

\- `app/safety/` — instruction gating and plan validation

\- `config/settings.json` — project configuration

\- `models/vosk/` — local Vosk model

\- `tests/` — automated tests

\- `logs/` — project logs



\## Run the Project



Activate the project's virtual environment, then run commands from the project root.



Typed instruction:



```powershell

python -m app.main

```



Voice instruction:



```powershell

python -m app.voice\_main

```



Run tests:



```powershell

python -m unittest discover -s tests -v

```



Test TTS independently:



```powershell

python -m app.tts.speaker

```



\## Safety Limitations



\- Physical motor control is disabled.

\- Robot actions are simulated only.

\- Review the recognized text and proposed plan before approving a voice command.

\- Do not approve commands when recognition or planning is uncertain.

\- Passing unit tests does not establish that the system is safe for physical deployment.



\## Not Yet Integrated or Verified



\- NVIDIA Riva ASR/TTS

\- Successful OpenClaw agent integration

\- Physical robot hardware control

\- Jetson deployment

\- Comprehensive voice-recognition accuracy evaluation

\- A successful end-to-end voice test through explicit approval and simulation



\## Future Work



1\. Verify the full voice pipeline with an accurately recognized command.

2\. Improve safety tests for malformed, ambiguous, and unexpected LLM plans.

3\. Complete project logging and create a backup archive.

4\. Plan and validate deployment on the target Jetson platform.

5\. Evaluate hardware integration only after simulation and safety requirements are satisfied.

