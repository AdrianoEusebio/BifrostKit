from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from bifrostkit.core.excecoes import ErroConfiguracao


class ConfiguracaoContexto(BaseModel):
    provedor_padrao: str = "manual"
    pasta_saida: str = "work"


class ConfiguracaoDocumentacao(BaseModel):
    pasta_saida: str = "docs"
    fontes: list[dict] = Field(default_factory=list)


class ConfiguracaoMcp(BaseModel):
    habilitado: bool = False
    pasta_mcps: str = "mcps"


class ConfiguracaoProjeto(BaseModel):
    nome: str
    descricao: Optional[str] = None
    contexto: ConfiguracaoContexto = Field(default_factory=ConfiguracaoContexto)
    documentacao: ConfiguracaoDocumentacao = Field(default_factory=ConfiguracaoDocumentacao)
    mcp: ConfiguracaoMcp = Field(default_factory=ConfiguracaoMcp)


"""
Carrega a configuração do projeto ativo seguindo a ordem de resolução:
1) Argumento explicitamente passado
2) Variável de ambiente KIT_PROJETO
3) Valor padrão: "exemplo"
"""
def carregar_projeto_ativo(nome_projeto: Optional[str] = None) -> ConfiguracaoProjeto:

    nome_resolvido = nome_projeto or os.getenv("KIT_PROJETO") or "exemplo"
    caminho_projeto = Path("projects") / f"{nome_resolvido}.yaml"

    if not caminho_projeto.exists():
        raise ErroConfiguracao(f"Configuração do projeto não encontrada: {caminho_projeto}")

    try:
        conteudo_raw = yaml.safe_load(caminho_projeto.read_text(encoding="utf-8")) or {}
        
        # Garante que o nome esteja no dict se não estiver no arquivo
        if "nome" not in conteudo_raw:
            conteudo_raw["nome"] = nome_resolvido

        return ConfiguracaoProjeto(**conteudo_raw)
    except Exception as e:
        raise ErroConfiguracao(f"Erro ao carregar projeto '{nome_resolvido}': {e}")
