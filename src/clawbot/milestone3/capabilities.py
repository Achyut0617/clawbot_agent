from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Capability:
    name: str
    handler: Callable[..., Any]
    required_permission: str
    enabled: bool = True
    sensitive: bool = False
    required_arguments: tuple[str, ...] = ()

class CapabilityDenied(PermissionError):
    pass

class CapabilityRegistry:
    def __init__(self):
        self._items: dict[str, Capability] = {}

    def register(self, capability: Capability):
        if not capability.name or capability.name in self._items:
            raise ValueError(f"Invalid or duplicate capability: {capability.name}")
        self._items[capability.name] = capability

    def get(self, name: str) -> Capability:
        item = self._items.get(name)
        if item is None or not item.enabled:
            raise CapabilityDenied(f"Unknown or disabled capability: {name}")
        return item

class CapabilityDispatcher:
    def __init__(self, registry: CapabilityRegistry, approval=None):
        self.registry = registry
        self.approval = approval or (lambda _name, _args: False)

    def dispatch(self, name: str, arguments: dict, permissions: frozenset[str]) -> dict:
        try:
            cap = self.registry.get(name)
            if not isinstance(arguments, dict):
                raise CapabilityDenied("Arguments must be an object")
            missing = set(cap.required_arguments) - set(arguments)
            if missing:
                raise CapabilityDenied(f"Missing arguments: {sorted(missing)}")
            if cap.required_permission not in permissions:
                raise CapabilityDenied("Required permission not granted")
            if cap.sensitive and not self.approval(name, arguments):
                raise CapabilityDenied("Explicit approval not granted")
            return {"success": True, "capability": name, "output": cap.handler(**arguments)}
        except Exception as exc:
            return {"success": False, "capability": name, "error": str(exc)}
