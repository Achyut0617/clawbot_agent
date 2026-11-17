from clawbot.safety import inspect_request


def test_empty_request_rejected():
    assert not inspect_request(" ").allowed


def test_request_requires_approval_by_default():
    decision = inspect_request("Summarize my project")
    assert decision.allowed
    assert decision.requires_approval


def test_approval_can_be_disabled_by_policy():
    decision = inspect_request("Explain Python", require_approval=False)
    assert decision.allowed
    assert not decision.requires_approval
