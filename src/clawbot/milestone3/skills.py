from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(frozen=True)
class SkillDescriptor:
    name: str
    description: str
    input_schema: dict[str, Any]
    enabled: bool = True

class OpenClawTransport(Protocol):
    # Implement using the documented Gateway/API contract for your OpenClaw version.
    async def list_skills(self) -> list[dict[str, Any]]: ...
    async def invoke_skill(self, name: str, arguments: dict[str, Any]) -> Any: ...

class SkillValidationError(ValueError):
    pass

class OpenClawSkillAdapter:
    def __init__(self, transport: OpenClawTransport):
        self.transport = transport
        self.skills: dict[str, SkillDescriptor] = {}

    async def discover(self) -> list[SkillDescriptor]:
        found = {}
        for item in await self.transport.list_skills():
            name, schema = item.get("name"), item.get("input_schema", {})
            if isinstance(name, str) and name and isinstance(schema, dict):
                found[name] = SkillDescriptor(name, str(item.get("description", "")),
                                              schema, bool(item.get("enabled", True)))
        self.skills = found
        return list(found.values())

    async def invoke(self, name: str, arguments: dict[str, Any]) -> Any:
        skill = self.skills.get(name)
        if skill is None or not skill.enabled:
            raise SkillValidationError(f"Unknown or disabled skill: {name}")
        if not isinstance(arguments, dict):
            raise SkillValidationError("Arguments must be an object")
        schema = skill.input_schema
        missing = set(schema.get("required", [])) - set(arguments)
        if missing:
            raise SkillValidationError(f"Missing arguments: {sorted(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(arguments) - set(properties)
            if extra:
                raise SkillValidationError(f"Unexpected arguments: {sorted(extra)}")
        return await self.transport.invoke_skill(name, arguments)
