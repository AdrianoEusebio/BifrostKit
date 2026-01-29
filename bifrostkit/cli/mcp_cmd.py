from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from bifrostkit.core.project import load_active_project
from bifrostkit.providers.mcp.registry import McpRegistry
from bifrostkit.providers.mcp.runner import McpRunner

app = typer.Typer(help="MCP commands (plugins via JSON, configs in pt-BR)")


@app.command("listar")
def list_mcps(
    project: Optional[str] = typer.Option(None, "--projeto", "-p", help="Nome do projeto (projects/<nome>.yaml)")
) -> None:
    project_cfg = load_active_project(project)
    registry = McpRegistry.from_folder(project_cfg.mcp_folder)

    if not registry.mcps:
        print("[yellow]Nenhum MCP encontrado.[/yellow]")
        return

    print(f"[bold]MCPs carregados[/bold] (pasta: {project_cfg.mcp_folder})")
    for mcp_id, mcp in registry.mcps.items():
        print(f" - [cyan]{mcp_id}[/cyan] :: {mcp.name} v{mcp.version}")
        for action in mcp.actions:
            print(f"    • [green]{action.key}[/green] — {action.title}")


@app.command("rodar")
def run_action(
    action_key: str = typer.Argument(..., help="Chave da ação MCP (ex: refinar_contexto)"),
    file_path: Optional[str] = typer.Option(None, "--arquivo", "-f", help="Caminho do arquivo para enviar ao MCP"),
    project: Optional[str] = typer.Option(None, "--projeto", "-p", help="Nome do projeto (projects/<nome>.yaml)"),
    timeout_seconds: int = typer.Option(60, "--timeout", help="Timeout em segundos"),
) -> None:
    project_cfg = load_active_project(project)
    if not project_cfg.mcp_enabled:
        print("[yellow]MCP está desabilitado neste projeto.[/yellow]")
        raise typer.Exit(code=2)

    registry = McpRegistry.from_folder(project_cfg.mcp_folder)
    resolved = registry.find_action(action_key)

    if resolved is None:
        print(f"[red]Ação não encontrada:[/red] {action_key}")
        raise typer.Exit(code=1)

    mcp, action = resolved
    input_file: Optional[Path] = Path(file_path).resolve() if file_path else None

    runner = McpRunner()
    result = runner.run_action(mcp=mcp, action=action, file_path=input_file, timeout_seconds=timeout_seconds)

    if result.stderr.strip():
        print("[yellow]MCP stderr:[/yellow]")
        print(result.stderr.strip())

    if not result.ok:
        print("[red]MCP returned ok=false.[/red]")
        print(result.response)
        raise typer.Exit(code=1)

    changed_path = runner.apply_output(action=action, result=result, input_file_path=input_file)
    print("[green]MCP executed successfully.[/green]")

    if changed_path is not None:
        print(f"[green]Updated file:[/green] {changed_path}")
    else:
        print("[cyan]No file was modified by output rules.[/cyan]")
