# Voice-Activated Clawbot Agent

## Project Overview

A locally running, voice-controlled robotic agent prototype developed using Python on Windows. The system integrates speech recognition, local LLM-powered instruction interpretation, structured action planning, safety validation, simulated robot execution, and text-to-speech feedback.

**Current Operating Mode:** Simulation only. Physical hardware and motor control are disabled.

## System Architecture

The agent follows a multi-stage processing pipeline:

### 1. Voice Input and Speech Recognition

**Microphone → Vosk Speech Recognition → Instruction Safety Gate**

- Captures voice commands through the microphone.
- Uses Vosk for offline speech-to-text conversion.
- Passes recognized instructions through an initial safety gate.
- Blocks ambiguous or potentially unsafe instructions and requests clarification when necessary.

### 2. AI-Based Action Planning

**Validated Instruction → Ollama (Qwen 2.5:1.5B) → Structured JSON Action Plan**

- Uses a locally hosted LLM through Ollama.
- Interprets natural-language instructions and determines the intended robot actions.
- Converts instructions into structured JSON action plans.
- Supports predefined robot actions with relevant parameters, such as movement direction and duration.

### 3. Safety Validation and Execution

**JSON Action Plan → Safety Validator → Simulated Robot Execution**

- Validates generated action plans against predefined safety rules.
- Rejects unsupported actions, invalid parameters, and unsafe execution requests.
- Allows only explicitly permitted actions to proceed.
- Executes approved actions in a simulated environment.
- Physical motor commands are not transmitted to any hardware.

### 4. Voice Feedback

**Execution Result → Text-to-Speech → Audio Feedback**

- Converts execution results into natural-language responses.
- Provides audio feedback about successful actions, rejected commands, or clarification requirements.
- Completes the interaction loop between the user and the robotic agent.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Speech Recognition | Vosk |
| Local LLM Runtime | Ollama |
| Language Model | Qwen 2.5 (1.5B) |
| Action Planning | Structured JSON |
| Safety Layer | Custom Python Safety Gate and Validator |
| Testing | Python `unittest` |
| Operating Environment | Windows |

## Safety and Execution Scope

The project implements a layered safety architecture:

1. **Instruction-Level Safety:** Filters ambiguous or unsafe natural-language commands.
2. **Plan-Level Validation:** Checks generated JSON action plans before execution.
3. **Execution Restriction:** Allows only supported actions in simulation mode.

**Important:** This is currently a software simulation prototype. Real-world robot movement, motor actuation, and hardware integration are not enabled.

## Project Objective

To develop a locally operated, voice-driven robotic agent that can understand natural-language instructions, translate them into structured actions, validate those actions through an independent safety layer, and provide interactive voice feedback without depending on cloud-based AI services.
