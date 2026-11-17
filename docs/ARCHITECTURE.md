# Architecture

```text
Voice (optional) ─┐
                  ├─> Input -> ClawBot Runtime -> Approval Policy -> OpenClaw CLI/Gateway
Keyboard/Text ────┘                 |                         |
                                    v                         v
                              SQLite ledger              OpenClaw agent,
                              audit events               sessions, skills, tools
                                    |
                                    v
                              terminal/TTS feedback
```

## Design rules
1. Voice and text use the same `AgentRuntime.submit()` path.
2. Microphone/ASR/TTS dependencies are optional; text is always available.
3. OpenClaw owns provider/model configuration and agent tool execution.
4. ClawBot stores task lifecycle and application audit events in SQLite.
5. Approval is required by default. The app does not run model-generated shell commands.
6. The existing robot simulation remains separate; physical actuation is out of scope.
