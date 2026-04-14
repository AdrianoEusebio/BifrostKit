from __future__ import annotations

from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from bifrostkit.core.configuracao import carregar_projeto_ativo
from bifrostkit.core.excecoes import ErroBifrostBase
from bifrostkit.servicos.servico_mcp import ServicoMcp

app = typer.Typer(help="Comandos MCP (plugins via JSON, servidores em Docker)")
console = Console()


@app.command("listar")
def listar_mcps(
    projeto: Optional[str] = typer.Option(
        None, "--projeto", "-p", help="Nome do projeto (projects/<nome>.yaml)"
    )
) -> None:
    """
    Lista todos os MCPs e ações disponíveis para o projeto atual.
    """
    try:
        projeto_cfg = carregar_projeto_ativo(projeto)
        servico = ServicoMcp(projeto_cfg)
        acoes = servico.listar_acoes_disponiveis()

        if not acoes:
            print("[yellow]Nenhuma ação MCP encontrada para este projeto.[/yellow]")
            return

        tabela = Table(title=f"Ações MCP Disponíveis (Projeto: {projeto_cfg.nome})")
        tabela.add_column("MCP", style="cyan")
        tabela.add_column("Chave da Ação", style="green")
        tabela.add_column("Título", style="white")

        for mcp, acao in acoes:
            tabela.add_row(mcp.nome, acao.chave, acao.titulo)

        console.print(tabela)

    except ErroBifrostBase as e:
        print(f"[red]Erro:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("rodar")
def rodar_acao(
    chave_acao: str = typer.Argument(..., help="Chave da ação MCP (ex: refinar_contexto)"),
    arquivo: Optional[str] = typer.Option(
        None, "--arquivo", "-f", help="Caminho do arquivo para enviar ao MCP"
    ),
    projeto: Optional[str] = typer.Option(
        None, "--projeto", "-p", help="Nome do projeto"
    ),
    timeout: int = typer.Option(60, "--timeout", help="Timeout em segundos"),
) -> None:
    """
    Executa uma ação específica de um MCP.
    """
    try:
        projeto_cfg = carregar_projeto_ativo(projeto)
        servico = ServicoMcp(projeto_cfg)

        with console.status(f"[bold green]Executando ação '{chave_acao}'..."):
            resultado, caminho_alterado = servico.executar(
                chave_acao=chave_acao, caminho_arquivo=arquivo, timeout=timeout
            )

        if not resultado.sucesso:
            print(f"[red]Falha na execução do MCP:[/red] {resultado.erro}")
            if resultado.dados:
                print(f"[dim]Dados de retorno: {resultado.dados}[/dim]")
            raise typer.Exit(code=1)

        print("[bold green]✓ Ação executada com sucesso![/bold green]")
        
        if caminho_alterado:
            print(f"  [blue]→ Arquivo atualizado:[/blue] {caminho_alterado}")
        else:
            print("  [cyan]i Nenhuma alteração de arquivo foi necessária.[/cyan]")

    except ErroBifrostBase as e:
        print(f"[red]Erro:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[red]Erro inesperado:[/red] {e}")
        raise typer.Exit(code=1)
