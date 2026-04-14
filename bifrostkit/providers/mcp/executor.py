from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from bifrostkit.core.excecoes import ErroExecucao
from bifrostkit.providers.mcp.modelos import AcaoMcp, ConfiguracaoServidorMcp
from bifrostkit.providers.mcp.transporte.base import TransporteBase
from bifrostkit.providers.mcp.transporte.docker_stdio import TransporteDockerStdio


@dataclass(frozen=True)
class ResultadoExecucaoMcp:
    sucesso: bool
    saida: str
    erro: str
    dados: Dict[str, Any]

"""
Coordenador de execução de ações MCP.
"""
class ExecutorMcp:

    def executar_acao(
        self,
        mcp: ConfiguracaoServidorMcp,
        acao: AcaoMcp,
        caminho_arquivo: Optional[Path] = None,
        timeout_segundos: int = 60,
    ) -> ResultadoExecucaoMcp:
        
        # Por enquanto, suportamos apenas docker-stdio
        if mcp.transporte.tipo != "docker-stdio":
            raise ErroExecucao(f"Tipo de transporte não suportado: {mcp.transporte.tipo}")

        transporte = TransporteDockerStdio()
        
        payload = self._montar_payload(acao=acao, caminho_arquivo=caminho_arquivo)

        try:
            resposta = transporte.enviar_requisicao(
                payload=payload,
                config=mcp.transporte,
                timeout_segundos=timeout_segundos,
            )

            sucesso = bool(resposta.get("ok", False))
            erro = str(resposta.get("erro", "")) if not sucesso else ""
            
            return ResultadoExecucaoMcp(
                sucesso=sucesso,
                saida=str(resposta.get("markdown", "")),
                erro=erro,
                dados=resposta,
            )
        except Exception as e:
            return ResultadoExecucaoMcp(
                sucesso=False,
                saida="",
                erro=str(e),
                dados={},
            )

    """
    Aplica as regras de saída definidas na ação (ex: sobrescrever o arquivo original).
    """
    def aplicar_saida(
        self,
        acao: AcaoMcp,
        resultado: ResultadoExecucaoMcp,
        caminho_entrada: Optional[Path],
    ) -> Optional[Path]:
        
        if not resultado.sucesso or not acao.saida:
            return None

        # Atualmente suportamos apenas o destino de sobrescrever entrada para markdown
        if acao.saida.tipo == "markdown" and acao.saida.destino == "sobrescrever_entrada":
            if caminho_entrada and resultado.saida:
                caminho_entrada.write_text(resultado.saida, encoding="utf-8")
                return caminho_entrada

        return None

    """
    Monta o payload para a ação MCP.
    """
    def _montar_payload(self, acao: AcaoMcp, caminho_arquivo: Optional[Path]) -> Dict[str, Any]:
        entradas: Dict[str, Any] = {}

        if caminho_arquivo is not None:
            conteudo = caminho_arquivo.read_text(encoding="utf-8")
            entradas["file"] = {
                "path": str(caminho_arquivo),
                "name": caminho_arquivo.name,
                "content": conteudo,
            }

        return {
            "action": acao.chave,
            "inputs": entradas,
        }

