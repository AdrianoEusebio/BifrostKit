from __future__ import annotations

import typer
from rich import print

from bifrostkit.cli.mcp_cmd import app as mcp_app

app = typer.Typer(
    help="BifrostKit - Automação de desenvolvimento (Contexto, Docs, Testes, DB, MCP)",
    rich_markup_mode="rich",
)

app.add_typer(mcp_app, name="mcp", help="Gerenciar e executar ações via MCP (Model Context Protocol)")


@app.callback()
def callback():
    """
    BifrostKit: Sua ponte para automação de desenvolvimento assistida por IA.
    """
    pass


# Submódulos futuros (esqueletos)
# app.add_typer(contexto_app, name="contexto", help="Gestão de arquivos de contexto")
# app.add_typer(docs_app, name="docs", help="Automação de documentação técnica")
# app.add_typer(jira_app, name="jira", help="Integração com Jira")
# app.add_typer(db_app, name="db", help="Interações e consultas em Banco de Dados")

if __name__ == "__main__":
    app()
