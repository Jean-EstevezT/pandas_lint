import click
import ast
import os
from rich.console import Console
from rich.table import Table
from .analyzer import PandasVisitor

console = Console()

@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    """
    Pandas-Linter: Static analyzer to optimize Data Science code.
    PATH can be a .py file or a directory.
    """
    files_to_check = []
    
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    files_to_check.append(os.path.join(root, file))
    else:
        files_to_check.append(path)

    total_issues = 0

    for file_path in files_to_check:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError as e:
                console.print(f"[bold red]Syntax error in {file_path}: {e}[/bold red]")
                continue

        visitor = PandasVisitor()
        visitor.visit(tree)

        if visitor.issues:
            total_issues += len(visitor.issues)
            print_report(file_path, visitor.issues)

    if total_issues > 0:
        console.print(f"\n[bold red] Found {total_issues} performance/memory issues.[/bold red]")
        exit(1)
    else:
        console.print("\n[bold green] Clean code! Good job.[/bold green]")
        exit(0)

def print_report(file_path, issues):
    table = Table(title=f"Analyzing: {file_path}")

    table.add_column("Line", justify="right", style="cyan", no_wrap=True)
    table.add_column("Code", style="magenta")
    table.add_column("Severity", style="bold")
    table.add_column("Message", style="white")

    for issue in issues:
        severity_style = "red" if issue.severity == "CRITICAL" else "yellow"
        table.add_row(
            str(issue.line),
            issue.code,
            f"[{severity_style}]{issue.severity}[/{severity_style}]",
            issue.message
        )

    console.print(table)