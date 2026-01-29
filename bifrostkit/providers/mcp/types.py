from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class McpTransportConfig:
    transport_type: str
    image: str
    command: List[str]
    env: Dict[str, str]


@dataclass(frozen=True)
class McpActionInput:
    name: str
    input_type: str
    required: bool


@dataclass(frozen=True)
class McpActionOutput:
    output_type: str
    target: str  # e.g. "overwrite_input"


@dataclass(frozen=True)
class McpActionConfig:
    key: str
    title: str
    description: str
    inputs: List[McpActionInput]
    output: Optional[McpActionOutput]


@dataclass(frozen=True)
class McpServerConfig:
    mcp_id: str
    name: str
    version: str
    transport: McpTransportConfig
    actions: List[McpActionConfig]
    hooks: Dict[str, str]


JsonDict = Dict[str, Any]
