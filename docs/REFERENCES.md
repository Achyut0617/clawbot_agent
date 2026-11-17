# Technical References and Source-of-Truth Policy

**Document ID:** `CB-DOC-010`  
**Project:** ClawBot Agent  
**Version:** 1.0.0  
**Status:** Engineering Reference

---

## 1. Purpose

This document maintains the technical references used to design, implement, test, secure, deploy, and maintain ClawBot.

It establishes a source-of-truth policy to prevent implementation decisions from relying on outdated tutorials, undocumented APIs, unverified compatibility claims, or assumptions about third-party software.

## 2. Reference categories

References are organized into the following categories:

| Category | Purpose |
|---|---|
| Architecture | System architecture and design principles |
| Orchestration | OpenClaw integration |
| Programming | Python and software engineering |
| Testing | Automated testing and validation |
| Security | Secure development and authorization |
| CI/CD | Build, test, and release automation |
| Persistence | Database and data management |
| Hardware | Embedded and accelerated platforms |
| Voice | Audio and speech processing |

## 3. OpenClaw references

OpenClaw is ClawBot's orchestration backend.

Official documentation must be the primary reference for installation, onboarding, Gateway behavior, supported interfaces, authentication, and compatibility.

| Resource | Purpose | Official URL |
|---|---|---|
| OpenClaw documentation | Main documentation | https://docs.openclaw.ai/ |
| Getting started | Installation and onboarding | https://docs.openclaw.ai/start/getting-started |
| Quickstart | First installation and Gateway setup | https://docs.openclaw.ai/quickstart |
| Gateway | Gateway operation and verification | https://docs.openclaw.ai/gateway |
| OpenClaw repository | Source code and releases | https://github.com/openclaw/openclaw |

### Integration policy

- Use documented and supported interfaces.
- Verify Gateway behavior against the installed OpenClaw version.
- Maintain an explicit compatibility record.
- Avoid depending on private implementation details.
- Revalidate the integration when upgrading OpenClaw.
- Do not assume that a CLI command, API, or protocol remains unchanged across releases.

OpenClaw's installation documentation currently specifies Node.js runtime requirements and platform-specific installation procedures. The exact supported versions must be checked against the official documentation at implementation time.

## 4. Python and packaging references

Python is the primary application implementation language.

| Resource | Purpose | Official URL |
|---|---|---|
| Python documentation | Language reference | https://docs.python.org/3/ |
| Python tutorial | Language fundamentals | https://docs.python.org/3/tutorial/ |
| Virtual environments | Isolated environments | https://docs.python.org/3/library/venv.html |
| Python packaging | Packaging guidance | https://packaging.python.org/ |
| Python logging | Application logging | https://docs.python.org/3/library/logging.html |
| Python typing | Type annotations | https://docs.python.org/3/library/typing.html |
| Python asyncio | Asynchronous programming | https://docs.python.org/3/library/asyncio.html |

### Engineering applications

Use these references when implementing:

- Runtime lifecycle.
- Async request processing.
- Adapter interfaces.
- Configuration management.
- Logging.
- Type contracts.
- Package distribution.
- Dependency isolation.

## 5. Testing references

| Resource | Purpose | Official URL |
|---|---|---|
| pytest | Python testing framework | https://docs.pytest.org/en/stable/ |
| unittest | Standard-library testing | https://docs.python.org/3/library/unittest.html |
| Coverage.py | Code coverage | https://coverage.readthedocs.io/ |
| Hypothesis | Property-based testing | https://hypothesis.readthedocs.io/ |

Testing references support:

- Unit testing.
- Integration testing.
- Parameterized tests.
- Fixtures.
- Test isolation.
- Property-based testing.
- Coverage analysis.

## 6. Security references

Security must be treated as a continuous engineering responsibility.

| Resource | Purpose | Official URL |
|---|---|---|
| OWASP Top 10 | Web application security risks | https://owasp.org/www-project-top-ten/ |
| OWASP API Security Top 10 | API security risks | https://owasp.org/www-project-api-security/ |
| OWASP Cheat Sheet Series | Secure implementation guidance | https://cheatsheetseries.owasp.org/ |
| NIST Cybersecurity Framework | Cybersecurity risk management | https://www.nist.gov/cyberframework |
| CWE | Common Weakness Enumeration | https://cwe.mitre.org/ |

### ClawBot security applications

These references should guide:

- Authentication.
- Authorization.
- Least privilege.
- Secure secret management.
- Input validation.
- API protection.
- Audit logging.
- Dependency security.
- Error handling.
- Secure execution boundaries.

OWASP guidance is a reference, not a substitute for a threat model specific to ClawBot.

## 7. CI/CD and source control references

| Resource | Purpose | Official URL |
|---|---|---|
| Git documentation | Version control | https://git-scm.com/doc |
| GitHub Actions | CI/CD workflows | https://docs.github.com/en/actions |
| Workflow syntax | Workflow configuration | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax |
| GitHub security | Repository security | https://docs.github.com/en/code-security |
| Semantic Versioning | Release version policy | https://semver.org/ |

These references guide:

- Branch management.
- Pull requests.
- Workflow configuration.
- Automated testing.
- Build artifacts.
- Release tagging.
- Version management.
- Dependency and repository security.

## 8. Persistence references

SQLite is the initial persistence backend.

| Resource | Purpose | Official URL |
|---|---|---|
| SQLite documentation | Database reference | https://www.sqlite.org/docs.html |
| SQLite SQL language | SQL syntax | https://www.sqlite.org/lang.html |
| SQLite transactions | Transaction management | https://www.sqlite.org/lang_transaction.html |
| SQLite backup API | Backup management | https://www.sqlite.org/backup.html |
| Python sqlite3 | Python database integration | https://docs.python.org/3/library/sqlite3.html |

These references should be used when implementing:

- Database initialization.
- Transactions.
- Task persistence.
- Event persistence.
- Database migrations.
- Backup and restore.
- Concurrency behavior.
- Recovery.

## 9. Hardware and edge computing references

ClawBot is intended to support multiple hardware classes. Platform compatibility must be validated against official hardware and software documentation.

| Resource | Purpose | Official URL |
|---|---|---|
| NVIDIA Jetson | Jetson platform documentation | https://developer.nvidia.com/embedded/jetson |
| Jetson Linux documentation | Jetson software platform | https://docs.nvidia.com/jetson/ |
| CUDA documentation | NVIDIA GPU computing | https://docs.nvidia.com/cuda/ |
| TensorRT documentation | NVIDIA inference optimization | https://docs.nvidia.com/deeplearning/tensorrt/ |
| Raspberry Pi documentation | Raspberry Pi platform | https://www.raspberrypi.com/documentation/ |
| Linux documentation | Linux kernel documentation | https://docs.kernel.org/ |

### Compatibility policy

A hardware platform is supported only when:

- Required runtime dependencies are compatible.
- Installation has been verified.
- Core application tests pass.
- Hardware-specific features have been tested.
- Known limitations are documented.

A detected GPU or ARM processor is not sufficient evidence of complete platform compatibility.

## 10. Voice and audio references

Voice implementation may involve operating-system audio devices, audio-processing libraries, speech recognition, and speech synthesis.

Reference documentation must be selected according to the actual adapters adopted by the project.

Relevant starting points:

| Resource | Purpose | Official URL |
|---|---|---|
| PortAudio | Cross-platform audio I/O | http://www.portaudio.com/docs.html |
| sounddevice | Python audio I/O | https://python-sounddevice.readthedocs.io/ |
| SpeechRecognition | Speech recognition library | https://github.com/Uberi/speech_recognition |
| Vosk | Offline speech recognition | https://alphacephei.com/vosk/ |
| Piper | Local text-to-speech project | https://github.com/OHF-Voice/piper1-gpl |

These are candidate technologies, not mandatory dependencies. Selection must consider licensing, platform compatibility, maintenance, privacy, performance, and resource consumption.

## 11. Reference validation policy

Every external technical reference used for implementation must be evaluated.

### 11.1 Validation checklist

- [ ] Is the source official?
- [ ] Is the documentation relevant to the installed version?
- [ ] Is the referenced API publicly supported?
- [ ] Are the installation instructions current?
- [ ] Are operating-system limitations documented?
- [ ] Are licensing conditions understood?
- [ ] Are security implications reviewed?
- [ ] Is the source still maintained?

### 11.2 Source priority

Use this priority order:

1. Official product documentation.
2. Official source-code repository and release notes.
3. Official standards and specifications.
4. Maintainer-authored technical explanations.
5. Reputable engineering publications.
6. Community discussions for supplementary troubleshooting.

Community examples must not override official interface contracts without verification.

## 12. Dependency decision records

Every major external dependency should have a documented decision record.

Example:

```yaml
dependency:
  id: DEP-OPENCLAW-001
  name: OpenClaw
  category: orchestration
  required: true

  purpose: External agent orchestration backend

  integration:
    method: documented_gateway_interface

  compatibility:
    verification_required: true
    version_policy: pinned_and_tested

  security:
    authentication_required: true
    secrets_in_source_control: false

  decision:
    status: accepted
    rationale: Central orchestration backend for ClawBot
```

This example describes the intended decision-record structure, not a verified compatibility declaration.

## 13. Technical decision records

Major architectural decisions must be documented separately.

Recommended location:

```text
docs/
    decisions/
        ADR-001-architecture.md
        ADR-002-orchestration-backend.md
        ADR-003-persistence.md
        ADR-004-voice-interface.md
        ADR-005-authorization-boundary.md
```

Each decision record should include:

- Decision identifier.
- Context.
- Problem statement.
- Alternatives considered.
- Selected approach.
- Rationale.
- Consequences.
- Status.
- Date.
- Related implementation tasks.

## 14. Reference maintenance

References must be reviewed when:

- A dependency is upgraded.
- An external API changes.
- A supported platform changes.
- A security issue affects an adopted dependency.
- A new capability is introduced.
- A previous technical assumption becomes invalid.

Broken or outdated references must be replaced with current official sources where possible.

## 15. Definition of Done

The reference system is complete when:

- [ ] Major dependencies have official documentation links.
- [ ] OpenClaw integration sources are documented.
- [ ] Security references are maintained.
- [ ] CI/CD references are available.
- [ ] Hardware references cover declared platforms.
- [ ] Voice technology references are documented.
- [ ] Dependency decisions are traceable.
- [ ] Architectural decisions have individual records.
- [ ] Outdated technical assumptions are reviewed.

**Engineering principle:** Every major technical decision must be explainable, traceable, and verifiable against a reliable source.
