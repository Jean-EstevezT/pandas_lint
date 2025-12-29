import click
import ast
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from .analyzer import PandasVisitor
from .notebook import parse_notebook
import concurrent.futures

console = Console()

def analyze_file(file_path):
    """
    Analyzes a single file and returns a list of issues.
    This function must be top-level to be picklable for multiprocessing.
    """
    issues = []
    cell_mapping = None
    file_content_lines = []
    
    try:
        if file_path.endswith(".ipynb"):
            code_content, cell_mapping = parse_notebook(file_path)
            tree = ast.parse(code_content)
            file_content_lines = code_content.splitlines()
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
                file_content_lines = content.splitlines()
                
        visitor = PandasVisitor()
        visitor.visit(tree)
        issues = visitor.issues
    except (SyntaxError, ValueError) as e:
        pass
        
    return file_path, issues, cell_mapping, file_content_lines

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
                if file.endswith(".py") or file.endswith(".ipynb"):
                    files_to_check.append(os.path.join(root, file))
    else:
        files_to_check.append(path)

    total_issues = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Analyzing {len(files_to_check)} files...", total=len(files_to_check))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(analyze_file, files_to_check)
            
            for file_path, issues, cell_mapping, file_content_lines in results:
                progress.advance(task)
                if issues:
                    total_issues += len(issues)
                    print_report(file_path, issues, cell_mapping, file_content_lines)

    if total_issues > 0:
        console.print(f"\n[bold red] Found {total_issues} performance/memory issues.[/bold red]")
        exit(1)
    else:
        console.print("\n[bold green] Clean code! Good job.[/bold green]")
        exit(0)

def print_report(file_path, issues, cell_mapping=None, file_content_lines=None):
    table = Table(title=f"Analyzing: {file_path}")

    table.add_column("Line", justify="right", style="cyan", no_wrap=True)
    table.add_column("Code", style="magenta", overflow="fold")
    table.add_column("Severity", style="bold")
    table.add_column("Message", style="white")

    for issue in issues:
        severity_style = "red" if issue.severity == "CRITICAL" else "yellow"
        
        line_display = str(issue.line)
        if cell_mapping and issue.line in cell_mapping:
            cell_idx = cell_mapping[issue.line]
            line_display = f"Cell {cell_idx + 1} : {issue.line}" 
        code_snippet = ""
        if file_content_lines and 0 <= issue.line - 1 < len(file_content_lines):
            raw_code = file_content_lines[issue.line - 1].strip()
            syntax = Syntax(raw_code, "python", theme="monokai", line_numbers=False)
            code_snippet = syntax

        table.add_row(
            line_display,
            code_snippet if code_snippet else issue.code,
            f"[{severity_style}]{issue.severity}[/{severity_style}]",
            issue.message
        )

    console.print(table)