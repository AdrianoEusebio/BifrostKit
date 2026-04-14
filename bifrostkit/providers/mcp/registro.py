from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from bifrostkit.providers.mcp.modelos import AcaoMcp, ConfiguracaoServidorMcp

"""
Carrega e gerencia as definições de servidores MCP a partir de pastas.
"""
class RegistroMcp:

    def __init__(self, mcps: Dict[str, ConfiguracaoServidorMcp]):
        self.mcps: Dict[str, ConfiguracaoServidorMcp] = mcps

    @classmethod
    def da_pasta(cls, caminho_pasta: str) -> RegistroMcp:
        pasta = Path(caminho_pasta)
        mcps_carregados: Dict[str, ConfiguracaoServidorMcp] = {}

        if not pasta.exists():
            return cls(mcps_carregados)

        for arquivo_json in pasta.glob("*.json"):
            try:
                dados_raw = json.loads(arquivo_json.read_text(encoding="utf-8"))

                # Pydantic valida o JSON automaticamente aqui
                config_mcp = ConfiguracaoServidorMcp(**dados_raw)
                mcps_carregados[config_mcp.id_mcp] = config_mcp
            except Exception:

                # Silenciosamente ignora arquivos JSON inválidos por enquanto
                continue

        return cls(mcps_carregados)

    """
    Busca em todos os MCPs registrados por uma ação com a chave informada.
    """
    def buscar_acao(self, chave_acao: str) -> Optional[Tuple[ConfiguracaoServidorMcp, AcaoMcp]]:
        
        for mcp in self.mcps.values():
            for acao in mcp.acoes:
                if acao.chave == chave_acao:
                    return mcp, acao
        return None

