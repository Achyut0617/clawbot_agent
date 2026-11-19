from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterable, Literal


@dataclass(frozen=True)
class ResponseEvent:
    kind: Literal["start", "delta", "complete", "error"]
    response_id: str
    text: str = ""
    sequence: int = 0


async def consume_response_stream(
    events: AsyncIterable[ResponseEvent],
    on_text,
    cancelled,
) -> str:
    \"\"\"Consume normalized response events. `on_text` receives each text delta.

    The OpenClaw adapter must translate the documented Gateway stream into these
    provider-neutral events. This function does not parse an invented wire format.
    \"\"\"
    assembled: list[str] = []
    expected_sequence = 0
    active_response: str | None = None

    async for event in events:
        if cancelled():
            break
        if active_response is None and event.kind == "start":
            active_response = event.response_id
        if active_response is not None and event.response_id != active_response:
            continue
        if event.kind == "delta":
            if event.sequence < expected_sequence:
                continue
            expected_sequence = event.sequence + 1
            assembled.append(event.text)
            on_text(event.text)
        elif event.kind == "error":
            raise RuntimeError(event.text or "Response stream failed")
        elif event.kind == "complete":
            break
        await asyncio.sleep(0)
    return "".join(assembled)
