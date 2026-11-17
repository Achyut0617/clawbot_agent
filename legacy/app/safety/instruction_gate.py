"""Conservative input checks before calling the local LLM."""

AMBIGUOUS_PHRASES = (
    "move motor to right",
    "move motor right",
    "move it right",
    "move motor to left",
    "move motor left",
)


def check_instruction(text):
    normalized = " ".join(text.lower().strip().split())

    if not normalized:
        return False, "Please enter an instruction."

    if normalized in AMBIGUOUS_PHRASES:
        return False, (
            "Please clarify: do you mean turn the robot right, "
            "or move a particular motor?"
        )

    return True, ""
