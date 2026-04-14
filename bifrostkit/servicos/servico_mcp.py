from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from bifrostkit.core.configuracao import ConfiguracaoProjeto
from bifrostkit.core.excecoes import ErroMcp
from bifrostkit.providers.mcp.executor import ExecutorMcp, ResultadoExecucaoMcp
from bifrostkit.providers.mcp.modelos import AcaoMcp, ConfiguracaoServidorMcp
from bifrostkit.providers.mcp.registro import RegistroMcp

"""
Serviço para gerenciar ações MCP.
"""
class ServicoMcp:
    def __init__(self, projeto: ConfiguracaoProjeto):
        self.projeto = projeto
        self.registro = RegistroMcp.da_pasta(projeto.mcp.pasta_mcps)
        self.executor = ExecutorMcp()

    """
    Retorna uma lista de todas as ações disponíveis em todos os MCPs registrados.
    """
    def listar_acoes_disponiveis(self) -> List[Tuple[ConfiguracaoServidorMcp, AcaoMcp]]:
        acoes = []
        for mcp in self.registro.mcps.values():
            for acao in mcp.acoes:
                acoes.append((mcp, acao))
        return acoes

    """
    Busca e executa uma ação MCP, aplicando as regras de saída se houver sucesso.
    """
    def executar(
        self,
        chave_acao: str,
        caminho_arquivo: Optional[str] = None,
        timeout: int = 60,
    ) -> Tuple[ResultadoExecucaoMcp, Optional[Path]]:
        
        if not self.projeto.mcp.habilitado:
            raise ErroMcp("O suporte a MCP está desabilitado nas configurações deste projeto.")

        resolucao = self.registro.buscar_acao(chave_acao)
        if not resolucao:
            raise ErroMcp(f"Ação MCP não encontrada: {chave_acao}")

        mcp, acao = resolucao
        caminho_entrada = Path(caminho_arquivo).resolve() if caminho_arquivo else None

        resultado = self.executor.executar_acao(
            mcp=mcp,
            acao=acao,
            caminho_arquivo=caminho_entrada,
            timeout_segundos=timeout,
        )

        caminho_alterado = self.executor.aplicar_saida(
            acao=acao,
            resultado=resultado,
            caminho_entrada=caminho_entrada,
        )

        return resultado, caminho_alterado

