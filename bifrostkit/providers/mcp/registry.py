from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from bifrostkit.providers.mcp.types import (
    JsonDict,
    McpActionConfig,
    McpActionInput,
    McpActionOutput,
    McpServerConfig,
    McpTransportConfig,
)


class McpRegistry:
    """
    Loads MCP definitions from JSON files in a folder.

    External MCP JSON uses pt-BR keys:
      - id, nome, versao, transporte, acoes, ganchos
      - actions: chave, titulo, descricao, entradas, saida
      - transport: tipo, imagem, comando, env
    """

    def __init__(self, mcps: Dict[str, McpServerConfig]):
        self.mcps: Dict[str, McpServerConfig] = mcps

    @classmethod
    def from_folder(cls, folder: str) -> "McpRegistry":
        base = Path(folder)
        mcps: Dict[str, McpServerConfig] = {}

        if not base.exists():
            return cls(mcps)

        for json_file in base.glob("*.json"):
            try:
                raw: JsonDict = json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            parsed = _parse_mcp_config(raw)
            if parsed is not None:
                mcps[parsed.mcp_id] = parsed

        return cls(mcps)

    def find_action(self, action_key: str) -> Optional[Tuple[McpServerConfig, McpActionConfig]]:
        for mcp in self.mcps.values():
            for action in mcp.actions:
                if action.key == action_key:
                    return mcp, action
        return None


def _parse_mcp_config(raw: Dict[str, Any]) -> Optional[McpServerConfig]:
    mcp_id = raw.get("id")
    if not isinstance(mcp_id, str) or not mcp_id.strip():
        return None

    name = str(raw.get("nome", mcp_id))
    version = str(raw.get("versao", "0.0.0"))

    transport_raw = raw.get("transporte", {}) or {}
    transport_type = str(transport_raw.get("tipo", "docker-stdio"))
    image = str(transport_raw.get("imagem", "")).strip()
    command = transport_raw.get("comando") or []
    env = transport_raw.get("env") or {}

    if not isinstance(command, list):
        command = []
    command = [str(x) for x in command]

    if not isinstance(env, dict):
        env = {}
    env = {str(k): str(v) for k, v in env.items()}

    transport = McpTransportConfig(
        transport_type=transport_type,
        image=image,
        command=command,
        env=env,
    )

    actions_raw = raw.get("acoes", []) or []
    actions: list[McpActionConfig] = []
    for a in actions_raw:
        if not isinstance(a, dict):
            continue

        key = str(a.get("chave", "")).strip()
        if not key:
            continue

        title = str(a.get("titulo", key))
        description = str(a.get("descricao", ""))

        inputs_raw = a.get("entradas", []) or []
        inputs: list[McpActionInput] = []
        for i in inputs_raw:
            if not isinstance(i, dict):
                continue
            inputs.append(
                McpActionInput(
                    name=str(i.get("nome", "")).strip(),
                    input_type=str(i.get("tipo", "texto")).strip(),
                    required=bool(i.get("obrigatorio", False)),
                )
            )
        inputs = [x for x in inputs if x.name]

        output_cfg: Optional[McpActionOutput] = None
        output_raw = a.get("saida")
        if isinstance(output_raw, dict):
            output_cfg = McpActionOutput(
                output_type=str(output_raw.get("tipo", "texto")),
                target=str(output_raw.get("destino", "")),
            )

        actions.append(
            McpActionConfig(
                key=key,
                title=title,
                description=description,
                inputs=inputs,
                output=output_cfg,
            )
        )

    hooks_raw = raw.get("ganchos") or {}
    if not isinstance(hooks_raw, dict):
        hooks_raw = {}
    hooks = {str(k): str(v) for k, v in hooks_raw.items()}

    return McpServerConfig(
        mcp_id=mcp_id,
        name=name,
        version=version,
        transport=transport,
        actions=actions,
        hooks=hooks,
    )
