"""
This module is to be used when updating ongoing novels.
It will download, format and post the downloaded chapters to the backend.
"""

import subprocess
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from stalkers_cli.core import Client, Format
from stalkers_cli.utils import OUTPUT_FOLDER_NAME, open_in_file_explorer


def print_responses_table(responses: list[dict]):
    """
    Responses array to rich table.
    """
    if not responses:
        print("[bold red]No responses to display.[/bold red]")
        return

    console = Console()

    table = Table(
        title=f"Updates {len(responses)}",
        show_lines=True,
        header_style="bold red",
        width=120
    )

    table.add_column("Slug", style="bold red", overflow='ellipsis')
    table.add_column("Message", overflow="fold")
    table.add_column("Source", overflow="fold")
    table.add_column("Chapters Count", style="green", overflow="fold")
    table.add_column("From", overflow="fold")
    table.add_column("To", overflow="fold")

    for res in responses:
        table.add_row(
            res.get("slug", ""),
            res.get("message", ""),
            res.get("source", ""),
            str(res.get("chapters_count", "")),
            str(res.get("from", "")),
            str(res.get("to", "")),
        )

    console.print(table)


def download_chapters_from_lncrawl(
    src_url: str, output_path: Path, start_index: int, end_index: int
):
    base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
    venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    lncrawl_script = base_dir / "lncrawl"

    cmd = [
        str(venv_python),
        str(lncrawl_script),
        "-s",
        src_url,
        "-o",
        str(output_path),
        "--filename_only",
        "--single",
        "--suppress",
        "--format",
        "json",
        "--close-directly",
        "--add-source-url",
        "--ignore-images",
        "--range",
        str(start_index),
        str(end_index),
    ]

    subprocess.run(cmd)


def download_format_post(response: dict, absolute_root: Path):
        novel_slug = response.get("slug")
        start_index = response.get("from")
        end_index = response.get("to")
        download_src = response.get("source")
        root_path = absolute_root / novel_slug

        download_chapters_from_lncrawl(
            src_url=download_src,
            output_path=root_path,
            start_index=start_index,
            end_index=end_index,
        )

        output_folder = root_path / OUTPUT_FOLDER_NAME

        # format_updates = typer.confirm("Format updates?", default=True)
        # if format_updates:
        format = Format(root_path=root_path, output_folder=output_folder)
        format.execute_range(range=(start_index, end_index))

        proceed_request = True

        if format.sus_chapters_count > 0:
            print(f"[yellow]Update has [red]{format.sus_chapters_count}[/red] SUS chapters[/yellow]")
            open_in_file_explorer(format.output_folder, default=False)
            proceed_request = typer.confirm(f"Proceed with POST Request?", default=True)
            
        if proceed_request:
            client = Client()
            client.post_chapter_in_bulk_request(chapters_file=format.output_file, novel_slug=novel_slug)


def all(responses: list[dict], absolute_root: Path):
    print_responses_table(responses)

    for index, response in enumerate(responses):
        novel_slug = response.get("slug")
        start_index = response.get("from")
        end_index = response.get("to")
        total = end_index-start_index
        
        print(
            f"[green][{index+1}/{len(responses)}] Downloading updates [yellow]({start_index} ~ {end_index} [{total+1}])[/yellow] for: [/green][blue]{novel_slug}[/blue]"
        )

        download_format_post(response, absolute_root)
        
        print("\n")