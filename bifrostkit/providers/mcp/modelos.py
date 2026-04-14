from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ConfiguracaoTransporteMcp(BaseModel):
    tipo: str = "docker-stdio"
    imagem: str
    comando: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class EntradaAcaoMcp(BaseModel):
    nome: str
    tipo: str = "texto"
    obrigatorio: bool = False


class SaidaAcaoMcp(BaseModel):
    tipo: str = "texto"
    destino: str = ""  # Ex: "sobrescrever_entrada"


class AcaoMcp(BaseModel):
    chave: str
    titulo: str
    descricao: str = ""
    entradas: list[EntradaAcaoMcp] = Field(default_factory=list, alias="entradas")
    saida: Optional[SaidaAcaoMcp] = None

    class Config:
        populate_by_name = True


class ConfiguracaoServidorMcp(BaseModel):
    id_mcp: str = Field(..., alias="id")
    nome: str
    versao: str = "0.0.0"
    transporte: ConfiguracaoTransporteMcp
    acoes: list[AcaoMcp] = Field(default_factory=list)
    ganchos: dict[str, str] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


# Aliases para facilitar uso interno
TipoJson = dict[str, Any]
