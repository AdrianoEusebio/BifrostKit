from __future__ import annotations

import typer

from bifrostkit.cli.mcp_cmd import app as mcp_app

app = typer.Typer(help="BifrostKit - dev automation (pt-BR configs, English code)")

app.add_typer(mcp_app, name="mcp")

# Next steps:
# app.add_typer(context_app, name="contexto")
# app.add_typer(docs_app, name="docs")
# app.add_typer(jira_app, name="jira")
# app.add_typer(db_app, name="db")
