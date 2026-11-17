# Security model

ClawBot is a controller around OpenClaw, not a sandbox. OpenClaw tools execute with the
permissions of the account running the Gateway.

## Required baseline
- Keep OpenClaw's gateway bound to localhost unless remote access is intentionally configured.
- Use OpenClaw's pairing/authentication and restrictive tool policies.
- Do not enable arbitrary shell, filesystem-wide, browser, or device-control tools by default.
- Keep credentials in OpenClaw's secret/config store or environment variables; never commit them.
- Review skills before installing them. Treat skill instructions and web content as untrusted.
- Keep ClawBot's `require_approval: true` until you have a capability-specific approval policy.
- Hardware control is disabled in this release. Do not connect real motors to the simulator.
- Use a dedicated OS account and a restricted workspace for agent operations.

ClawBot's approval gate is a coarse application-level gate. It does not replace OpenClaw
tool-level authorization, OS permissions, container isolation, or human review.
