from __future__ import annotations

import json
import subprocess
import time
from typing import Any, Dict, Optional, Tuple

from bifrostkit.core.excecoes import ErroExecucao
from bifrostkit.providers.mcp.transporte.base import TransporteBase


"""
Implementação de transporte que executa um container Docker e se comunica
via entrada e saída padrão (stdio) usando JSON.
"""
class TransporteDockerStdio(TransporteBase):

    """
    Envia uma requisição para o MCP.
    """
    def enviar_requisicao(
        self,
        payload: Dict[str, Any],
        config: Any,  # Esperado ConfiguracaoTransporteMcp
        timeout_segundos: int = 60,
    ) -> Dict[str, Any]:
        
        imagem = config.imagem
        comando = config.comando
        env = config.env

        if not imagem:
            raise ErroExecucao("A imagem Docker é obrigatória para o transporte docker-stdio.")

        # Constrói o comando docker
        comando_docker = ["docker", "run", "--rm", "-i"]
        for k, v in env.items():
            comando_docker.extend(["-e", f"{k}={v}"])
        comando_docker.append(imagem)
        if comando:
            comando_docker.extend(comando)

        json_input = json.dumps(payload, ensure_ascii=False) + "\n"

        proc = subprocess.Popen(
            comando_docker,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        try:
            stdout, stderr = proc.communicate(input=json_input, timeout=timeout_segundos)
            resposta = self._extrair_json(stdout)
            
            if resposta is None:
                detalhes_erro = stderr.strip() or "Nenhum JSON retornado pelo servidor MCP."
                return {"ok": False, "erro": f"Resposta inválida do MCP. Detalhes: {detalhes_erro}"}

            return resposta

        except subprocess.TimeoutExpired:
            proc.kill()
            return {"ok": False, "erro": "Timeout na execução do container Docker."}

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise ErroExecucao(f"Falha ao executar transporte Docker: {e}")

    """
    Tenta encontrar a primeira linha que contenha um JSON válido.
    Muitas vezes servidores MCP emitem logs antes de enviar o JSON final.
    """
    def _extrair_json(self, texto_saida: str) -> Optional[Dict[str, Any]]:
        
        linhas = [linha.strip() for linha in texto_saida.splitlines() if linha.strip()]
        for linha in linhas:
            try:
                objeto = json.loads(linha)
                if isinstance(objeto, dict):
                    return objeto
            except json.JSONDecodeError:
                continue
        return None
