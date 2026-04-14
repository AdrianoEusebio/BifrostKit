from __future__ import annotations


"""
Classe base para todas as exceções do BifrostKit.
"""
class ErroBifrostBase(Exception):

    pass


"""
Lançada quando há um erro no carregamento ou validação das configurações.
"""
class ErroConfiguracao(ErroBifrostBase):

    pass


"""
Lançada quando ocorre um erro durante a execução de um processo ou comando.
"""
class ErroExecucao(ErroBifrostBase):

    pass


"""
Lançada para erros específicos relacionados ao MCP (Registro, Execução, etc).
"""
class ErroMcp(ErroBifrostBase):

    pass
