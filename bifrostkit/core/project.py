from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    """
    Internal project config (English field names).
    External config remains in pt-BR keys (projects/*.yaml).
    """

    name: str
    description: Optional[str]
    context_output_dir: str
    docs_output_dir: str
    mcp_enabled: bool
    mcp_folder: str


def load_active_project(project_name: Optional[str] = None) -> ProjectConfig:
    """
    Resolution order:
      1) --projeto argument
      2) KIT_PROJETO environment variable
      3) fallback: "exemplo"
    """
    resolved_name = project_name or os.getenv("KIT_PROJETO") or "exemplo"
    project_path = Path("projects") / f"{resolved_name}.yaml"

    if not project_path.exists():
        raise FileNotFoundError(f"Project config not found: {project_path}")

    raw: dict[str, Any] = yaml.safe_load(project_path.read_text(encoding="utf-8")) or {}

    # External keys in pt-BR
    context = raw.get("contexto", {}) or {}
    docs = raw.get("documentacao", {}) or {}
    mcp = raw.get("mcp", {}) or {}

    return ProjectConfig(
        name=str(raw.get("nome", resolved_name)),
        description=raw.get("descricao"),
        context_output_dir=str(context.get("pasta_saida", "work")),
        docs_output_dir=str(docs.get("pasta_saida", "docs")),
        mcp_enabled=bool(mcp.get("habilitado", False)),
        mcp_folder=str(mcp.get("pasta_mcps", "mcps")),
    )
