# Development workflow

1. Pick an atomic item from `ROADMAP.yaml`.
2. Create a branch: `feat/VOICE-002-wake-word`.
3. Implement one independently testable change.
4. Add/update tests and docs.
5. Run `ruff check .` and `pytest`.
6. Update the roadmap status and commit mapping.
7. Open a PR; CI must pass before merge.

Commit format: `type(ATOMIC-ID): imperative summary`

Suggested types: `feat`, `fix`, `test`, `docs`, `refactor`, `perf`, `ci`, `build`.
