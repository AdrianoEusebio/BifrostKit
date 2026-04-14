from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


"""
Interface abstrata que define como o BifrostKit se comunica com um servidor MCP.
"""
class TransporteBase(ABC):

    """
    Envia uma requisição JSON para o transporte e retorna a resposta JSON.
    """
    @abstractmethod
    def enviar_requisicao(
        self,
        payload: Dict[str, Any],
        config: Any,
        timeout_segundos: int = 60,
    ) -> Dict[str, Any]:
        pass
